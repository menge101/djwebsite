from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Class
from basilico.elements import Div, Text
from lib import return_, session, threading, types
from typing import cast
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## About act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying about template")
def apply_template(text: str) -> str:
    template = Div(
        Class("hero bg-base-200 min-h-96 w-2/3 tab-content m-auto"), Div(Class("hero-content text-center"), Text(text))
    )
    return template.string()


@xray_recorder.capture("## Building about body")
def build(
    connection_thread: threading.ReturningThread, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting about build")
    localization: str = session_data.get("local", "en")
    text_body: str = get_data(connection_thread, localization)
    return return_.http(body=apply_template(text_body), status_code=200)


@xray_recorder.capture("## Getting about data")
def get_data(connection_thread: threading.ReturningThread, localization: str) -> str:
    logger.debug("Getting about data")
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    response = ddb_client.get_item(
        TableName=table_name,
        Key={"pk": {"S": localization}, "sk": {"S": "section#body#about"}},
    )
    return lens.focus(response, ["Item", "text", "S"])
