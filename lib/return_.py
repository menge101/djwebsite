from aws_xray_sdk.core import xray_recorder
from typing import cast, NewType, Optional
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

Returnable = NewType("Returnable", dict[str, bool | dict | int | str])


@xray_recorder.capture("### Returning error")
def error(exception: Exception, status_code: int, headers: Optional[dict[str, str]] = None) -> Returnable:
    body = f"<div>\nError: {str(exception)}\n</div>"
    headers = headers or {}
    return http(body, status_code, headers)


@xray_recorder.capture("### Returning non-error")
def http(
    body: str,
    status_code: int,
    headers: Optional[dict[str, list[str]]] = None,
    cookies: Optional[list[str]] = None,
) -> Returnable:
    headers = headers or {}
    cookies = cookies or []
    headers["Content-Type"] = ["text/html"]
    if cookies:
        headers["Set-Cookie"] = cookies
    response = cast(
        Returnable,
        {
            "statusCode": status_code,
            "body": body,
            "multiValueHeaders": headers,
        },
    )
    logger.debug(f"Response: {response}")
    return response
