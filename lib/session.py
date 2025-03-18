from aws_xray_sdk.core import xray_recorder
from datetime import datetime
from lib import cookie, return_, threading, types
from typing import cast, NewType, Optional
from uuid import uuid1
import botocore.exceptions
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


SessionData = NewType("SessionData", dict[str, dict[str, str] | str])


# Important, the key "id_" SHOULD NOT BE SET in these defaults, "id_" only gets set by code downstream from here
DEFAULT_SESSION_VALUES: SessionData = SessionData(
    {
        "pk": "session",
        "translate": {"state": "closed", "local": "en"},
    }
)


@xray_recorder.capture("## Creating session maybe")
def act(
    connection_thread: threading.ReturningThread,
    session_data: SessionData,
    _query_params: dict[str, str],
) -> tuple[SessionData, list[str]]:
    session_id = session_data.get("id_", None)
    if session_id:
        logger.debug("session exists")
        return session_data, ["session-found"]
    logger.debug("session does not exist")
    session_id = str(uuid1())
    exp = cookie.expiration_time(24 * 60 * 60)
    session_data = cast(SessionData, DEFAULT_SESSION_VALUES.copy())
    session_data["sk"] = session_id
    session_data["id_"] = session_id
    session_data["ttl"] = str(cookie.expiration_as_ttl(exp))
    update_session(connection_thread=connection_thread, session_data=session_data)
    return session_data, ["session-created"]


@xray_recorder.capture("## Building session element")
def build(
    _connection_thread: threading.ReturningThread,
    session_data: SessionData,
    *_args,
    **_kwargs,
) -> return_.Returnable:
    logger.debug(f"Session build: {session_data}")
    if not session_data:
        raise ValueError("Session should be set by act function, prior to build call")
    try:
        session_id: str = cast(str, session_data["id_"])
        session_ttl: int = int(cast(str, session_data["ttl"]))
    except KeyError as ke:
        logger.exception(ke)
        logger.error(f"Unexpected lack of session data pieces: {session_data}")
        raise ValueError("Session should be set by act function, prior to build call")
    exp = datetime.fromtimestamp(session_ttl)
    session_cookie = cookie.Cookie(
        "id_",
        session_id,
        secure=True,
        http_only=True,
        expires=exp,
        same_site="Strict",
    )
    logger.debug(f"Session cookie set: {session_cookie}")
    return return_.http("", 200, cookies=[str(session_cookie)])


@xray_recorder.capture("## Retrieving session data from ddb table")
def get_session_data(session_id: str, table_connection_thread: threading.ReturningThread) -> SessionData:
    _, _, tbl = cast(types.ConnectionThreadResultType, table_connection_thread.join())
    response = tbl.get_item(Key={"pk": "session", "sk": session_id}, ConsistentRead=True)
    logger.debug(f"Session data: {response['Item']}")
    return cast(SessionData, response["Item"])


@xray_recorder.capture("## Decoding session ID from cookie")
def get_session_id_from_cookies(event: dict) -> str:
    raw_cookies = event.get("cookies", [])
    cookies = {}
    for raw in raw_cookies:
        key, value = raw.split("=", 1)
        cookies[key] = value
    return cookies["id_"]


@xray_recorder.capture("## Handling session data")
def handle_session(event: dict, table_connection_thread: threading.ReturningThread) -> SessionData:
    try:
        session_id = get_session_id_from_cookies(event)
    except KeyError:
        return DEFAULT_SESSION_VALUES
    return get_session_data(session_id, table_connection_thread)


@xray_recorder.capture("## Creating/Updating session data")
def update_session(connection_thread: threading.ReturningThread, session_data: dict[str, Optional[str]]) -> None:
    logger.debug("Writing session to ddb")
    logger.debug(f"Session data: {session_data}")
    _, _, ddb_tbl = cast(types.ConnectionThreadResultType, connection_thread.join())
    try:
        ddb_tbl.put_item(Item=session_data)
    except botocore.exceptions.ClientError as ce:
        logger.exception(ce)
        logger.error("Failed to write session data")
        raise ValueError("Improperly formatted session data, likely stemming from session corruption") from ce
    logger.debug(f"Session written to ddb: {session_data}")
