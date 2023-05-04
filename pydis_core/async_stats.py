"""An async transport method for statsd communication."""

import asyncio
import socket
from typing import Optional

from statsd.client.base import StatsClientBase

from pydis_core.utils import scheduling


class AsyncStatsClient(StatsClientBase):
    """An async implementation of :obj:`statsd.client.base.StatsClientBase` that supports async stat communication."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        host: str = 'localhost',
        port: int = 8125,
        prefix: str = None
    ):
        """
        Create a new :obj:`AsyncStatsClient`.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop to use when creating the
                :obj:`asyncio.loop.create_datagram_endpoint`.
            host: The host to connect to.
            port: The port to connect to.
            prefix: The prefix to use for all stats.
        """
        _, _, _, _, addr = socket.getaddrinfo(
            host, port, socket.AF_INET, socket.SOCK_DGRAM
        )[0]
        self._addr = addr
        self._prefix = prefix
        self._loop = loop
        self._transport: Optional[asyncio.DatagramTransport] = None

    async def create_socket(self) -> None:
        """Use :obj:`asyncio.loop.create_datagram_endpoint` from the loop given on init to create a socket."""
        self._transport, _ = await self._loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            family=socket.AF_INET,
            remote_addr=self._addr
        )

    def _send(self, data: str) -> None:
        """Start an async task to send data to statsd."""
        scheduling.create_task(self._async_send(data), event_loop=self._loop)

    async def _async_send(self, data: str) -> None:
        """Send data to the statsd server using the async transport."""
        self._transport.sendto(data.encode('ascii'), self._addr)


__all__ = ['AsyncStatsClient']
