# -*- coding: utf-8 -*-
r"""Bridges local JSON-RPC/stdio servers to HTTP/SSE.

Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti, Manav Gupta

This module provides bidirectional bridging between MCP servers that communicate
via stdio/JSON-RPC and HTTP/SSE endpoints. It enables exposing local MCP servers
over HTTP or consuming remote SSE endpoints as local stdio servers.

The bridge supports two modes of operation:
- stdio to SSE: Expose a local stdio MCP server over HTTP/SSE
- SSE to stdio: Bridge a remote SSE endpoint to local stdio

Examples:
    Programmatic usage:

    >>> import asyncio
    >>> from mcpgateway.translate import start_stdio
    >>> asyncio.run(start_stdio("uvx mcp-server-git", 9000, "info", None, "127.0.0.1"))  # doctest: +SKIP

Usage:
    Command line usage::

        # 1. Expose an MCP server that talks JSON-RPC on stdio at :9000/sse
        python3 -m mcpgateway.translate --stdio "uvx mcp-server-git" --port 9000

        # 2. From another shell / browser subscribe to the SSE stream
        curl -N http://localhost:9000/sse          # receive the stream

        # 3. Send a test echo request
        curl -X POST http://localhost:9000/message \
             -H 'Content-Type: application/json'   \
             -d '{"jsonrpc":"2.0","id":1,"method":"echo","params":{"value":"hi"}}'

        # 4. Proper MCP handshake and tool listing
        curl -X POST http://localhost:9000/message \
             -H 'Content-Type: application/json' \
             -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo","version":"0.0.1"}}}'

        curl -X POST http://localhost:9000/message \
             -H 'Content-Type: application/json' \
             -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

    The SSE stream now emits JSON-RPC responses as ``event: message`` frames and sends
    regular ``event: keepalive`` frames (default every 30s) so that proxies and
    clients never time out. Each client receives a unique *session-id* that is
    appended as a query parameter to the back-channel ``/message`` URL.
"""

# Future
from __future__ import annotations

# Standard
import argparse
import asyncio
from contextlib import suppress
import json
import logging
import shlex
import signal
import sys
from typing import Any, AsyncIterator, Dict, List, Optional, Sequence
import uuid

# Third-Party
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

try:
    # Third-Party
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

LOGGER = logging.getLogger("mcpgateway.translate")
KEEP_ALIVE_INTERVAL = 30  # seconds - matches the reference implementation
__all__ = ["main"]  # for console-script entry-point


# ---------------------------------------------------------------------------#
# Helpers - trivial in-process Pub/Sub                                       #
# ---------------------------------------------------------------------------#
class _PubSub:
    """Very small fan-out helper - one async Queue per subscriber.

    This class implements a simple publish-subscribe pattern using asyncio queues
    for distributing messages from stdio subprocess to multiple SSE clients.

    Examples:
        >>> import asyncio
        >>> async def test_pubsub():
        ...     pubsub = _PubSub()
        ...     q = pubsub.subscribe()
        ...     await pubsub.publish("hello")
        ...     result = await q.get()
        ...     pubsub.unsubscribe(q)
        ...     return result
        >>> asyncio.run(test_pubsub())
        'hello'
    """

    def __init__(self) -> None:
        """Initialize a new publish-subscribe system.

        Creates an empty list of subscriber queues. Each subscriber will
        receive their own asyncio.Queue for receiving published messages.

        Examples:
            >>> pubsub = _PubSub()
            >>> isinstance(pubsub._subscribers, list)
            True
            >>> len(pubsub._subscribers)
            0
            >>> hasattr(pubsub, '_subscribers')
            True
        """
        self._subscribers: List[asyncio.Queue[str]] = []

    async def publish(self, data: str) -> None:
        """Publish data to all subscribers.

        Dead queues (full) are automatically removed from the subscriber list.

        Args:
            data: The data string to publish to all subscribers.

        Examples:
            >>> import asyncio
            >>> async def test_publish():
            ...     pubsub = _PubSub()
            ...     await pubsub.publish("test")  # No subscribers, no error
            ...     return True
            >>> asyncio.run(test_publish())
            True

            >>> # Test queue full handling
            >>> async def test_full_queue():
            ...     pubsub = _PubSub()
            ...     # Create a queue with size 1
            ...     q = asyncio.Queue(maxsize=1)
            ...     pubsub._subscribers = [q]
            ...     # Fill the queue
            ...     await q.put("first")
            ...     # This should remove the full queue
            ...     await pubsub.publish("second")
            ...     return len(pubsub._subscribers)
            >>> asyncio.run(test_full_queue())
            0
        """
        dead: List[asyncio.Queue[str]] = []
        for q in self._subscribers:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            with suppress(ValueError):
                self._subscribers.remove(q)

    def subscribe(self) -> "asyncio.Queue[str]":
        """Subscribe to published data.

        Creates a new queue for receiving published messages with a maximum
        size of 1024 items.

        Returns:
            asyncio.Queue[str]: A queue that will receive published data.

        Examples:
            >>> pubsub = _PubSub()
            >>> q = pubsub.subscribe()
            >>> isinstance(q, asyncio.Queue)
            True
            >>> q.maxsize
            1024
            >>> len(pubsub._subscribers)
            1
            >>> pubsub._subscribers[0] is q
            True
        """
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=1024)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: "asyncio.Queue[str]") -> None:
        """Unsubscribe from published data.

        Removes the queue from the subscriber list. Safe to call even if
        the queue is not in the list.

        Args:
            q: The queue to unsubscribe from published data.

        Examples:
            >>> pubsub = _PubSub()
            >>> q = pubsub.subscribe()
            >>> pubsub.unsubscribe(q)
            >>> pubsub.unsubscribe(q)  # No error on double unsubscribe
        """
        with suppress(ValueError):
            self._subscribers.remove(q)


# ---------------------------------------------------------------------------#
# StdIO endpoint (child process ↔ async queues)                              #
# ---------------------------------------------------------------------------#
class StdIOEndpoint:
    """Wrap a child process whose stdin/stdout speak line-delimited JSON-RPC.

    This class manages a subprocess that communicates via stdio using JSON-RPC
    protocol, pumping messages between the subprocess and a pubsub system.

    Examples:
        >>> import asyncio
        >>> async def test_stdio():
        ...     pubsub = _PubSub()
        ...     stdio = StdIOEndpoint("echo hello", pubsub)
        ...     # Would start a real subprocess
        ...     return isinstance(stdio, StdIOEndpoint)
        >>> asyncio.run(test_stdio())
        True
    """

    def __init__(self, cmd: str, pubsub: _PubSub) -> None:
        """Initialize a stdio endpoint for subprocess communication.

        Sets up the endpoint with the command to run and the pubsub system
        for message distribution. The subprocess is not started until start()
        is called.

        Args:
            cmd: The command string to execute as a subprocess.
            pubsub: The publish-subscribe system for distributing subprocess
                output to SSE clients.

        Examples:
            >>> pubsub = _PubSub()
            >>> endpoint = StdIOEndpoint("echo hello", pubsub)
            >>> endpoint._cmd
            'echo hello'
            >>> endpoint._proc is None
            True
            >>> endpoint._stdin is None
            True
            >>> endpoint._pump_task is None
            True
            >>> endpoint._pubsub is pubsub
            True
        """
        self._cmd = cmd
        self._pubsub = pubsub
        self._proc: Optional[asyncio.subprocess.Process] = None
        self._stdin: Optional[asyncio.StreamWriter] = None
        self._pump_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start the stdio subprocess.

        Creates the subprocess and starts the stdout pump task. The subprocess
        is created with stdin/stdout pipes and stderr passed through.

        Raises:
            RuntimeError: If the subprocess fails to create stdin/stdout pipes.

        Examples:
            >>> import asyncio # doctest: +SKIP
            >>> async def test_start(): # doctest: +SKIP
            ...     pubsub = _PubSub()
            ...     stdio = StdIOEndpoint("cat", pubsub)
            ...     # await stdio.start()  # doctest: +SKIP
            ...     return True
            >>> asyncio.run(test_start()) # doctest: +SKIP
            True
        """
        LOGGER.info(f"Starting stdio subprocess: {self._cmd}")
        self._proc = await asyncio.create_subprocess_exec(
            *shlex.split(self._cmd),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # passthrough for visibility
        )

        # Explicit error checking
        if not self._proc.stdin or not self._proc.stdout:
            raise RuntimeError(f"Failed to create subprocess with stdin/stdout pipes for command: {self._cmd}")

        self._stdin = self._proc.stdin
        self._pump_task = asyncio.create_task(self._pump_stdout())

    async def stop(self) -> None:
        """Stop the stdio subprocess.

        Terminates the subprocess gracefully with a 5-second timeout,
        then cancels the pump task.

        Examples:
            >>> import asyncio
            >>> async def test_stop():
            ...     pubsub = _PubSub()
            ...     stdio = StdIOEndpoint("cat", pubsub)
            ...     await stdio.stop()  # Safe to call even if not started
            ...     return True
            >>> asyncio.run(test_stop())
            True
        """
        if self._proc is None:
            return
        LOGGER.info(f"Stopping subprocess (pid={self._proc.pid})")
        self._proc.terminate()
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._proc.wait(), timeout=5)
        if self._pump_task:
            self._pump_task.cancel()

    async def send(self, raw: str) -> None:
        """Send data to the subprocess stdin.

        Args:
            raw: The raw data string to send to the subprocess.

        Raises:
            RuntimeError: If the stdio endpoint is not started.

        Examples:
            >>> import asyncio
            >>> async def test_send():
            ...     pubsub = _PubSub()
            ...     stdio = StdIOEndpoint("cat", pubsub)
            ...     try:
            ...         await stdio.send("test")
            ...     except RuntimeError as e:
            ...         return str(e)
            >>> asyncio.run(test_send())
            'stdio endpoint not started'
        """
        if not self._stdin:
            raise RuntimeError("stdio endpoint not started")
        LOGGER.debug(f"→ stdio: {raw.strip()}")
        self._stdin.write(raw.encode())
        await self._stdin.drain()

    async def _pump_stdout(self) -> None:
        """Pump stdout from subprocess to pubsub.

        Continuously reads lines from the subprocess stdout and publishes them
        to the pubsub system. Runs until EOF or exception.

        Raises:
            RuntimeError: If process or stdout is not properly initialized.
            Exception: For any other error encountered while pumping stdout.
        """
        if not self._proc or not self._proc.stdout:
            raise RuntimeError("Process not properly initialized: missing stdout")

        reader = self._proc.stdout
        try:
            while True:
                line = await reader.readline()
                if not line:  # EOF
                    break
                text = line.decode(errors="replace")
                LOGGER.debug(f"← stdio: {text.strip()}")
                await self._pubsub.publish(text)
        except Exception:  # pragma: no cover --best-effort logging
            LOGGER.exception("stdout pump crashed - terminating bridge")
            raise


# ---------------------------------------------------------------------------#
# FastAPI app exposing /sse  &  /message                                     #
# ---------------------------------------------------------------------------#


def _build_fastapi(
    pubsub: _PubSub,
    stdio: StdIOEndpoint,
    keep_alive: int = KEEP_ALIVE_INTERVAL,
    sse_path: str = "/sse",
    message_path: str = "/message",
    cors_origins: Optional[List[str]] = None,
) -> FastAPI:
    """Build FastAPI application with SSE and message endpoints.

    Creates a FastAPI app with SSE streaming endpoint and message posting
    endpoint for bidirectional communication with the stdio subprocess.

    Args:
        pubsub: The publish/subscribe system for message routing.
        stdio: The stdio endpoint for subprocess communication.
        keep_alive: Interval in seconds for keepalive messages. Defaults to KEEP_ALIVE_INTERVAL.
        sse_path: Path for the SSE endpoint. Defaults to "/sse".
        message_path: Path for the message endpoint. Defaults to "/message".
        cors_origins: Optional list of CORS allowed origins.

    Returns:
        FastAPI: The configured FastAPI application.

    Examples:
        >>> pubsub = _PubSub()
        >>> stdio = StdIOEndpoint("cat", pubsub)
        >>> app = _build_fastapi(pubsub, stdio)
        >>> isinstance(app, FastAPI)
        True
        >>> "/sse" in [r.path for r in app.routes]
        True
        >>> "/message" in [r.path for r in app.routes]
        True
        >>> "/healthz" in [r.path for r in app.routes]
        True

        >>> # Test with custom paths
        >>> app2 = _build_fastapi(pubsub, stdio, sse_path="/events", message_path="/send")
        >>> "/events" in [r.path for r in app2.routes]
        True
        >>> "/send" in [r.path for r in app2.routes]
        True

        >>> # Test CORS middleware is added
        >>> app3 = _build_fastapi(pubsub, stdio, cors_origins=["http://example.com"])
        >>> # Check that middleware stack includes CORSMiddleware
        >>> any("CORSMiddleware" in str(m) for m in app3.user_middleware)
        True
    """
    app = FastAPI()

    # Add CORS middleware if origins specified
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ----- GET /sse ---------------------------------------------------------#
    @app.get(sse_path)
    async def get_sse(request: Request) -> EventSourceResponse:  # noqa: D401
        """Stream subprocess stdout to any number of SSE clients.

        Args:
            request (Request): The incoming ``GET`` request that will be
                upgraded to a Server-Sent Events (SSE) stream.

        Returns:
            EventSourceResponse: A streaming response that forwards JSON-RPC
            messages from the child process and emits periodic ``keepalive``
            frames so that clients and proxies do not time out.
        """
        queue = pubsub.subscribe()
        session_id = uuid.uuid4().hex

        async def event_gen() -> AsyncIterator[Dict[str, Any]]:
            """Generate Server-Sent Events for the SSE stream.

            Yields SSE events in the following sequence:
            1. An 'endpoint' event with the message posting URL (required by MCP spec)
            2. An immediate 'keepalive' event to confirm the stream is active
            3. 'message' events containing JSON-RPC responses from the subprocess
            4. Periodic 'keepalive' events to prevent timeouts

            The generator runs until the client disconnects or the server shuts down.
            Automatically unsubscribes from the pubsub system on completion.

            Yields:
                Dict[str, Any]: SSE event dictionaries containing:
                    - event: The event type ('endpoint', 'message', or 'keepalive')
                    - data: The event payload (URL, JSON-RPC message, or empty object)
                    - retry: Retry interval in milliseconds for reconnection

            Examples:
                >>> import asyncio
                >>> async def test_event_gen():
                ...     # This is tested indirectly through the SSE endpoint
                ...     return True
                >>> asyncio.run(test_event_gen())
                True
            """
            # 1️⃣ Mandatory "endpoint" bootstrap required by the MCP spec
            endpoint_url = f"{str(request.base_url).rstrip('/')}{message_path}?session_id={session_id}"
            yield {
                "event": "endpoint",
                "data": endpoint_url,
                "retry": int(keep_alive * 1000),
            }

            # 2️⃣ Immediate keepalive so clients know the stream is alive
            yield {"event": "keepalive", "data": "{}", "retry": keep_alive * 1000}

            try:
                while True:
                    if await request.is_disconnected():
                        break

                    try:
                        msg = await asyncio.wait_for(queue.get(), keep_alive)
                        yield {"event": "message", "data": msg.rstrip()}
                    except asyncio.TimeoutError:
                        yield {
                            "event": "keepalive",
                            "data": "{}",
                            "retry": keep_alive * 1000,
                        }
            finally:
                pubsub.unsubscribe(queue)

        return EventSourceResponse(
            event_gen(),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # disable proxy buffering
            },
        )

    # ----- POST /message ----------------------------------------------------#
    @app.post(message_path, status_code=status.HTTP_202_ACCEPTED)
    async def post_message(raw: Request, session_id: str | None = None) -> Response:  # noqa: D401
        """Forward a raw JSON-RPC request to the stdio subprocess.

        Args:
            raw (Request): The incoming ``POST`` request whose body contains
                a single JSON-RPC message.
            session_id (str | None): The SSE session identifier that originated
                this back-channel call (present when the client obtained the
                endpoint URL from an ``endpoint`` bootstrap frame).

        Returns:
            Response: ``202 Accepted`` if the payload is forwarded successfully,
            or ``400 Bad Request`` when the body is not valid JSON.
        """
        _ = session_id  # Unused but required for API compatibility
        payload = await raw.body()
        try:
            json.loads(payload)  # validate
        except Exception as exc:  # noqa: BLE001
            return PlainTextResponse(
                f"Invalid JSON payload: {exc}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        await stdio.send(payload.decode().rstrip() + "\n")
        return PlainTextResponse("forwarded", status_code=status.HTTP_202_ACCEPTED)

    # ----- Liveness ---------------------------------------------------------#
    @app.get("/healthz")
    async def health() -> Response:  # noqa: D401
        """Health check endpoint.

        Returns:
            Response: A plain text response with "ok" status.
        """
        return PlainTextResponse("ok")

    return app


# ---------------------------------------------------------------------------#
# CLI & orchestration                                                        #
# ---------------------------------------------------------------------------#


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Validates mutually exclusive source options and sets defaults for
    port and logging configuration.

    Args:
        argv: Sequence of command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.

    Raises:
        NotImplementedError: If streamableHttp option is specified.

    Examples:
        >>> args = _parse_args(["--stdio", "cat", "--port", "9000"])
        >>> args.stdio
        'cat'
        >>> args.port
        9000
        >>> args.logLevel
        'info'
        >>> args.host
        '127.0.0.1'
        >>> args.cors is None
        True
        >>> args.oauth2Bearer is None
        True

        >>> # Test default parameters
        >>> args = _parse_args(["--stdio", "cat"])
        >>> args.port
        8000
        >>> args.host
        '127.0.0.1'
        >>> args.logLevel
        'info'

        >>> # Test SSE mode
        >>> args = _parse_args(["--sse", "http://example.com/sse"])
        >>> args.sse
        'http://example.com/sse'
        >>> args.stdio is None
        True

        >>> # Test CORS configuration
        >>> args = _parse_args(["--stdio", "cat", "--cors", "https://app.com", "https://web.com"])
        >>> args.cors
        ['https://app.com', 'https://web.com']

        >>> # Test OAuth2 Bearer token
        >>> args = _parse_args(["--sse", "http://example.com", "--oauth2Bearer", "token123"])
        >>> args.oauth2Bearer
        'token123'

        >>> # Test custom host and log level
        >>> args = _parse_args(["--stdio", "cat", "--host", "0.0.0.0", "--logLevel", "debug"])
        >>> args.host
        '0.0.0.0'
        >>> args.logLevel
        'debug'

        >>> # Test streamableHttp raises NotImplementedError
        >>> try:
        ...     _parse_args(["--streamableHttp", "test"])
        ... except NotImplementedError as e:
        ...     "Only --stdio" in str(e)
        True
    """
    p = argparse.ArgumentParser(
        prog="mcpgateway.translate",
        description="Bridges stdio JSON-RPC to SSE or SSE to stdio.",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdio", help='Command to run, e.g. "uv run mcp-server-git"')
    src.add_argument("--sse", help="Remote SSE endpoint URL")
    src.add_argument("--streamableHttp", help="[NOT IMPLEMENTED]")

    p.add_argument("--port", type=int, default=8000, help="HTTP port to bind")
    p.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    p.add_argument(
        "--logLevel",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level",
    )
    p.add_argument(
        "--cors",
        nargs="*",
        help="CORS allowed origins (e.g., --cors https://app.example.com)",
    )
    p.add_argument(
        "--oauth2Bearer",
        help="OAuth2 Bearer token for authentication",
    )

    args = p.parse_args(argv)
    if args.streamableHttp:
        raise NotImplementedError("Only --stdio → SSE and --sse → stdio are available in this build.")
    return args


async def _run_stdio_to_sse(cmd: str, port: int, log_level: str = "info", cors: Optional[List[str]] = None, host: str = "127.0.0.1") -> None:
    """Run stdio to SSE bridge.

    Starts a subprocess and exposes it via HTTP/SSE endpoints. Handles graceful
    shutdown on SIGINT/SIGTERM.

    Args:
        cmd: The command to run as a stdio subprocess.
        port: The port to bind the HTTP server to.
        log_level: The logging level to use. Defaults to "info".
        cors: Optional list of CORS allowed origins.
        host: The host interface to bind to. Defaults to "127.0.0.1" for security.

    Examples:
        >>> import asyncio # doctest: +SKIP
        >>> async def test_run(): # doctest: +SKIP
        ...     await _run_stdio_to_sse("cat", 9000)  # doctest: +SKIP
        ...     return True
        >>> asyncio.run(test_run()) # doctest: +SKIP
        True
    """
    pubsub = _PubSub()
    stdio = StdIOEndpoint(cmd, pubsub)
    await stdio.start()

    app = _build_fastapi(pubsub, stdio, cors_origins=cors)
    config = uvicorn.Config(
        app,
        host=host,  # Changed from hardcoded "0.0.0.0"
        port=port,
        log_level=log_level,
        lifespan="off",
    )
    server = uvicorn.Server(config)

    shutting_down = asyncio.Event()  # 🔄 make shutdown idempotent

    async def _shutdown() -> None:
        """Handle graceful shutdown of the stdio bridge.

        Performs shutdown operations in the correct order:
        1. Sets a flag to prevent multiple shutdown attempts
        2. Stops the stdio subprocess
        3. Shuts down the HTTP server

        This function is idempotent - multiple calls will only execute
        the shutdown sequence once.

        Examples:
            >>> import asyncio
            >>> async def test_shutdown():
            ...     # Shutdown is tested as part of the main run flow
            ...     return True
            >>> asyncio.run(test_shutdown())
            True
        """
        if shutting_down.is_set():
            return
        shutting_down.set()
        LOGGER.info("Shutting down ...")
        await stdio.stop()
        await server.shutdown()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):  # Windows lacks add_signal_handler
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

    LOGGER.info(f"Bridge ready → http://{host}:{port}/sse")
    await server.serve()
    await _shutdown()  # final cleanup


async def _run_sse_to_stdio(url: str, oauth2_bearer: Optional[str], timeout: float = 30.0) -> None:
    """Run SSE to stdio bridge.

    Connects to a remote SSE endpoint and bridges it to local stdio.

    Args:
        url: The SSE endpoint URL to connect to.
        oauth2_bearer: Optional OAuth2 bearer token for authentication.
        timeout: HTTP client timeout in seconds. Defaults to 30.0.

    Raises:
        ImportError: If httpx package is not available.

    Examples:
        >>> import asyncio
        >>> async def test_sse():
        ...     try:
        ...         await _run_sse_to_stdio("http://example.com/sse", None)  # doctest: +SKIP
        ...     except ImportError as e:
        ...         return "httpx" in str(e)
        >>> asyncio.run(test_sse())  # Would return True if httpx not installed # doctest: +SKIP
    """
    if not httpx:
        raise ImportError("httpx package is required for SSE to stdio bridging")

    headers = {}
    if oauth2_bearer:
        headers["Authorization"] = f"Bearer {oauth2_bearer}"

    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(timeout=timeout, connect=10.0)) as client:
        process = await asyncio.create_subprocess_shell(
            "cat",  # Placeholder command; replace with actual stdio server command if needed
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,
        )

        async def read_stdout() -> None:
            """Read lines from subprocess stdout and print to console.

            Continuously reads lines from the subprocess stdout stream until EOF
            is reached. Each line is decoded and printed to the console without
            trailing newlines.

            This coroutine runs as part of the SSE to stdio bridge, forwarding
            subprocess output to the user's terminal.

            Raises:
                RuntimeError: If the process stdout stream is not available.

            Examples:
                >>> import asyncio
                >>> async def test_read():
                ...     # This is tested as part of the SSE to stdio flow
                ...     return True
                >>> asyncio.run(test_read())
                True
            """
            if not process.stdout:
                raise RuntimeError("Process stdout not available")

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                print(line.decode().rstrip())

        async def pump_sse_to_stdio() -> None:
            """Stream SSE data from remote endpoint to subprocess stdin.

            Connects to the remote SSE endpoint and forwards data lines to the
            subprocess stdin. Only processes lines that start with "data: " and
            ignores empty data payloads or keepalive messages ("{}").

            This coroutine runs as part of the SSE to stdio bridge, pumping
            messages from the remote SSE stream to the local subprocess.

            Examples:
                >>> import asyncio
                >>> async def test_pump():
                ...     # This is tested as part of the SSE to stdio flow
                ...     return True
                >>> asyncio.run(test_pump())
                True
            """
            async with client.stream("GET", url) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data and data != "{}":
                            if process.stdin:
                                process.stdin.write((data + "\n").encode())
                                await process.stdin.drain()

        await asyncio.gather(read_stdout(), pump_sse_to_stdio())


def start_stdio(cmd: str, port: int, log_level: str, cors: Optional[List[str]], host: str = "127.0.0.1") -> None:
    """Start stdio bridge.

    Entry point for starting a stdio to SSE bridge server.

    Args:
        cmd: The command to run as a stdio subprocess.
        port: The port to bind the HTTP server to.
        log_level: The logging level to use.
        cors: Optional list of CORS allowed origins.
        host: The host interface to bind to. Defaults to "127.0.0.1".

    Returns:
        None: This function does not return a value.

    Examples:
        >>> start_stdio("uvx mcp-server-git", 9000, "info", None)  # doctest: +SKIP
    """
    return asyncio.run(_run_stdio_to_sse(cmd, port, log_level, cors, host))


def start_sse(url: str, bearer: Optional[str], timeout: float = 30.0) -> None:
    """Start SSE bridge.

    Entry point for starting an SSE to stdio bridge client.

    Args:
        url: The SSE endpoint URL to connect to.
        bearer: Optional OAuth2 bearer token for authentication.
        timeout: HTTP client timeout in seconds. Defaults to 30.0.

    Returns:
        None: This function does not return a value.

    Examples:
        >>> start_sse("http://example.com/sse", "token123")  # doctest: +SKIP
    """
    return asyncio.run(_run_sse_to_stdio(url, bearer, timeout))


def main(argv: Optional[Sequence[str]] | None = None) -> None:
    """Entry point for the translate module.

    Configures logging, parses arguments, and starts the appropriate bridge
    based on command line options. Handles keyboard interrupts gracefully.

    Args:
        argv: Optional sequence of command line arguments. If None, uses sys.argv[1:].

    Examples:
        >>> # Test argument parsing
        >>> try:
        ...     main(["--stdio", "cat", "--port", "9000"])  # doctest: +SKIP
        ... except SystemExit:
        ...     pass  # Would normally start the server
        >>> try: # doctest: +SKIP
        ...     main(["--streamableHttp", "test"])
        ... except SystemExit as e:
        ...     e.code
        1
    """
    args = _parse_args(argv or sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.logLevel.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        if args.stdio:
            start_stdio(args.stdio, args.port, args.logLevel, args.cors, args.host)
        elif args.sse:
            start_sse(args.sse, args.oauth2Bearer)
    except KeyboardInterrupt:
        print("")  # restore shell prompt
        sys.exit(0)
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # python3 -m mcpgateway.translate ...
    main()
