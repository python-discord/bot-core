import json
from typing import TypedDict

from aiohttp import ClientConnectorError, ClientSession

from pydis_core.utils import logging

log = logging.get_logger(__name__)

DEFAULT_PASTEBIN = "https://paste.pythondiscord.com"
FAILED_REQUEST_ATTEMPTS = 3
MAX_PASTE_SIZE = 512 * 1024  # 512kB
"""The maximum allows size of a paste, in bytes."""

# A dict where the keys are paste services and the keys are the lists of lexers that paste service supports.
_lexers_supported_by_pastebin: dict[str,list[str]] = {}


class PasteResponse(TypedDict):
    """
    A successful response from the paste service.

    args:
        link: The URL to the saved paste.
        removal: The URL to delete the saved paste.
    """

    link: str
    removal: str


class PasteUploadError(Exception):
    """Raised when an error is encountered uploading to the paste service."""

class PasteUnsupportedLexerError(Exception):
    """Raised when an unsupported lexer is used."""


class PasteTooLongError(Exception):
    """Raised when content is too large to upload to the paste service."""


async def send_to_paste_service(
    *,
    contents: str,
    http_session: ClientSession,
    file_name: str = "",
    lexer: str = "python",
    paste_url: str = DEFAULT_PASTEBIN,
    max_size: int = MAX_PASTE_SIZE,
) -> PasteResponse:
    """
    Upload some contents to the paste service.

    Args:
        contents: The content to upload to the paste service.
        http_session (aiohttp.ClientSession): The session to use when POSTing the content to the paste service.
        file_name: The name of the file to save to the paste service.
        lexer: The lexer to save the content with.
        paste_url: The base url to the paste service.
        max_size: The max number of bytes to be allowed. Anything larger than :obj:`MAX_PASTE_SIZE` will be rejected.

    Raises:
        :exc:`ValueError`: ``max_length`` greater than the maximum allowed by the paste service.
        :exc:`PasteTooLongError`: ``contents`` too long to upload.
        :exc:`PasteUploadError`: Uploading failed.

    Returns:
        A :obj:`TypedDict` containing both the URL of the paste, and a URL to remove the paste.
    """
    if max_size > MAX_PASTE_SIZE:
        raise ValueError(f"`max_length` must not be greater than {MAX_PASTE_SIZE}")

    if paste_url not in _lexers_supported_by_pastebin:
        try:
            async with http_session.get(f"{paste_url}/api/v1/lexer") as response:
                response_json = await response.json()  # Supported lexers are the keys.
        except Exception:
            raise PasteUploadError("Could not fetch supported lexers from selected paste_url.")

        _lexers_supported_by_pastebin[paste_url] = list(response_json)

    if lexer not in _lexers_supported_by_pastebin[paste_url]:
        raise PasteUnsupportedLexerError(f"Lexer '{lexer}' not supported by pastebin.")

    contents_size = len(contents.encode())
    if contents_size > max_size:
        log.info("Contents too large to send to paste service.")
        raise PasteTooLongError(f"Contents of size {contents_size} greater than maximum size {max_size}")

    log.debug(f"Sending contents of size {contents_size} bytes to paste service.")
    payload = {
        "expiry": "1month",
        "long": "on",  # Use a longer URI for the paste.
        "files": [
            {"name": file_name, "lexer": lexer, "content": contents},
        ]
    }
    for attempt in range(1, FAILED_REQUEST_ATTEMPTS + 1):
        try:
            async with http_session.post(f"{paste_url}/api/v1/paste", json=payload) as response:
                response_text = await response.text()
        except ClientConnectorError:
            log.warning(
                f"Failed to connect to paste service at url {paste_url}, "
                f"trying again ({attempt}/{FAILED_REQUEST_ATTEMPTS})."
            )
            continue
        except Exception:
            log.exception(
                f"An unexpected error has occurred during handling of the request, "
                f"trying again ({attempt}/{FAILED_REQUEST_ATTEMPTS})."
            )
            continue

        if "Text exceeds size limit" in response_text:
            log.info("Contents too large to send to paste service after lexing.")
            raise PasteTooLongError(
                f"Contents of size {contents_size} greater than maximum size {max_size} after lexing"
            )

        response_json = json.loads(response_text)
        if response.status == 400:
            log.warning(
                f"Paste service returned error {response_json['message']} with status code {response.status}, "
                f"trying again ({attempt}/{FAILED_REQUEST_ATTEMPTS})."
            )
            continue

        if response.status == 200:
            log.info(f"Successfully uploaded contents to {response_json['link']}.")
            return PasteResponse(link=response_json["link"], removal=response_json["removal"])

        log.warning(
            f"Got unexpected JSON response from paste service: {response_json}\n"
            f"trying again ({attempt}/{FAILED_REQUEST_ATTEMPTS})."
        )

    raise PasteUploadError("Failed to upload contents to paste service")
