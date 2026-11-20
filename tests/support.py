"""Helpers to exercise the Redis server over a real TCP socket."""

from __future__ import annotations

import asyncio
import socket
import threading
from typing import BinaryIO

from app.connection import handle_client

CRLF = b"\r\n"


class RedisError(Exception):
    """Reply the server sent as a RESP error (`-ERR ...`)."""


class ProtocolError(Exception):
    """Reply the test client could not parse."""


def encode(*parts: str | bytes) -> bytes:
    """Encode one command as a RESP array of bulk strings."""
    chunks = [part.encode() if isinstance(part, str) else part for part in parts]
    out = bytearray(b"*" + str(len(chunks)).encode() + CRLF)
    for chunk in chunks:
        out += b"$" + str(len(chunk)).encode() + CRLF + chunk + CRLF
    return bytes(out)


def read_reply(stream: BinaryIO):
    """Read one RESP2 reply from a binary stream."""
    line = stream.readline()
    if not line:
        raise EOFError("connection closed before a reply arrived")
    if not line.endswith(CRLF):
        raise ProtocolError(f"incomplete reply line: {line!r}")

    kind, payload = line[:1], line[1:-2]

    if kind == b"+":
        return payload.decode()
    if kind == b"-":
        raise RedisError(payload.decode())
    if kind == b":":
        return int(payload)
    if kind == b"$":
        length = int(payload)
        if length == -1:
            return None
        data = stream.read(length + 2)
        if len(data) != length + 2 or not data.endswith(CRLF):
            raise ProtocolError(f"incomplete bulk string: {data!r}")
        return data[:-2]
    if kind == b"*":
        length = int(payload)
        if length == -1:
            return None
        return [read_reply(stream) for _ in range(length)]

    raise ProtocolError(f"unknown reply type: {line!r}")


class Connection:
    """A blocking test client for one server connection."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self._stream = sock.makefile("rb")

    def send(self, *parts: str | bytes) -> None:
        """Send one complete command."""
        self.send_raw(encode(*parts))

    def send_raw(self, data: bytes) -> None:
        """Send raw bytes, e.g. a command split across packets."""
        self._sock.sendall(data)

    def read(self):
        """Read one complete reply."""
        return read_reply(self._stream)

    def read_line(self) -> bytes:
        """Read a single raw line, for cases where RESP is not enough."""
        return self._stream.readline()

    def close(self) -> None:
        self._stream.close()
        self._sock.close()

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


class ServerHarness:
    """Run the real connection handler on a free local port.

    The server lives in a background event loop, so tests stay synchronous and
    never fight with a manual server on port 6379.
    """

    def __init__(self, handler=handle_client, host: str = "127.0.0.1") -> None:
        self._handler = handler
        self._host = host
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._server: asyncio.AbstractServer | None = None
        self.port: int | None = None

    def __enter__(self) -> "ServerHarness":
        self._thread.start()
        self._server = asyncio.run_coroutine_threadsafe(
            self._start(), self._loop
        ).result(timeout=5)
        if not self._server.sockets:
            raise RuntimeError("server started without a listening socket")
        self.port = self._server.sockets[0].getsockname()[1]
        return self

    async def _start(self) -> asyncio.AbstractServer:
        return await asyncio.start_server(self._handler, self._host, 0)

    def connect(self, timeout: float = 2.0) -> Connection:
        if self.port is None:
            raise RuntimeError("ServerHarness must be used as a context manager")
        sock = socket.create_connection((self._host, self.port), timeout=timeout)
        return Connection(sock)

    def __exit__(self, *exc_info: object) -> None:
        if self._server is not None:
            asyncio.run_coroutine_threadsafe(
                self._stop(), self._loop
            ).result(timeout=5)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        self._loop.close()

    async def _stop(self) -> None:
        assert self._server is not None
        self._server.close()
