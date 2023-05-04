"""An API wrapper around the Site API."""

import asyncio
from typing import Optional
from urllib.parse import quote as quote_url

import aiohttp

from pydis_core.utils.logging import get_logger

log = get_logger(__name__)


class ResponseCodeError(ValueError):
    """Raised in :meth:`APIClient.request` when a non-OK HTTP response is received."""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        response_json: Optional[dict] = None,
        response_text: Optional[str] = None
    ):
        """
        Initialize a new :obj:`ResponseCodeError` instance.

        Args:
            response (:obj:`aiohttp.ClientResponse`): The response object from the request.
            response_json: The JSON response returned from the request, if any.
            response_text: The text of the request, if any.
        """
        self.status = response.status
        self.response_json = response_json or {}
        self.response_text = response_text
        self.response = response

    def __str__(self):
        """Return a string representation of the error."""
        response = self.response_json or self.response_text
        return f"Status: {self.status} Response: {response}"


class APIClient:
    """A wrapper for the Django Site API."""

    session: Optional[aiohttp.ClientSession] = None
    loop: asyncio.AbstractEventLoop = None

    def __init__(self, site_api_url: str, site_api_token: str, **session_kwargs):
        """
        Initialize a new :obj:`APIClient` instance.

        Args:
            site_api_url: The URL of the site API.
            site_api_token: The token to use for authentication.
            session_kwargs: Keyword arguments to pass to the :obj:`aiohttp.ClientSession` constructor.
        """
        self.site_api_url = site_api_url

        auth_headers = {
            'Authorization': f"Token {site_api_token}"
        }

        if 'headers' in session_kwargs:
            session_kwargs['headers'].update(auth_headers)
        else:
            session_kwargs['headers'] = auth_headers

        # aiohttp will complain if APIClient gets instantiated outside a coroutine. Thankfully, we
        # don't and shouldn't need to do that, so we can avoid scheduling a task to create it.
        self.session = aiohttp.ClientSession(**session_kwargs)

    def _url_for(self, endpoint: str) -> str:
        return f"{self.site_api_url}/{quote_url(endpoint)}"

    async def close(self) -> None:
        """Close the aiohttp session."""
        await self.session.close()

    @staticmethod
    async def maybe_raise_for_status(response: aiohttp.ClientResponse, should_raise: bool) -> None:
        """
        Raise :exc:`ResponseCodeError` for non-OK response if an exception should be raised.

        Args:
            response (:obj:`aiohttp.ClientResponse`): The response to check.
            should_raise: Whether or not to raise an exception.

        Raises:
            :exc:`ResponseCodeError`:
                If the response is not OK and ``should_raise`` is True.
        """
        if should_raise and response.status >= 400:
            try:
                response_json = await response.json()
                raise ResponseCodeError(response=response, response_json=response_json)
            except aiohttp.ContentTypeError:
                response_text = await response.text()
                raise ResponseCodeError(response=response, response_text=response_text)

    async def request(self, method: str, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> dict:
        """
        Send an HTTP request to the site API and return the JSON response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to send the request to.
            raise_for_status: Whether or not to raise an exception if the response is not OK.
            **kwargs: Any extra keyword arguments to pass to :func:`aiohttp.request`.

        Returns:
            The JSON response the API returns.

        Raises:
            :exc:`ResponseCodeError`:
                If the response is not OK and ``raise_for_status`` is True.
        """
        async with self.session.request(method.upper(), self._url_for(endpoint), **kwargs) as resp:
            await self.maybe_raise_for_status(resp, raise_for_status)
            return await resp.json()

    async def get(self, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> dict:
        """Equivalent to :meth:`APIClient.request` with GET passed as the method."""
        return await self.request("GET", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def patch(self, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> dict:
        """Equivalent to :meth:`APIClient.request` with PATCH passed as the method."""
        return await self.request("PATCH", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def post(self, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> dict:
        """Equivalent to :meth:`APIClient.request` with POST passed as the method."""
        return await self.request("POST", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def put(self, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> dict:
        """Equivalent to :meth:`APIClient.request` with PUT passed as the method."""
        return await self.request("PUT", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def delete(self, endpoint: str, *, raise_for_status: bool = True, **kwargs) -> Optional[dict]:
        """
        Send a DELETE request to the site API and return the JSON response.

        Args:
            endpoint: The endpoint to send the request to.
            raise_for_status: Whether or not to raise an exception if the response is not OK.
            **kwargs: Any extra keyword arguments to pass to :func:`aiohttp.request`.

        Returns:
            The JSON response the API returns, or None if the response is 204 No Content.
        """
        async with self.session.delete(self._url_for(endpoint), **kwargs) as resp:
            if resp.status == 204:
                return None

            await self.maybe_raise_for_status(resp, raise_for_status)
            return await resp.json()


__all__ = ['APIClient', 'ResponseCodeError']
