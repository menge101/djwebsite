from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Class, Src
from basilico.elements import Div, Element, IFrame
from lib import return_, session, threading, types
from typing import cast
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Mix:
    def __init__(self, src: str):
        self.src = src

    def render(self) -> Element:
        return IFrame(Class("h-auto w-full"), Src(self.src))


@xray_recorder.capture("## Mixes act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying mixes template")
def apply_template(mixes: list[Mix]) -> str:
    template = Div(Class("tab w-2/3 m-auto space-y-16"), *(mix.render() for mix in mixes))
    return template.string()


@xray_recorder.capture("## Building mix body")
def build(connection_thread: threading.ReturningThread, *_args, **_kwargs) -> return_.Returnable:
    logger.debug("Starting mixes build")
    mixes = get_data(connection_thread)
    return return_.http(body=apply_template(mixes), status_code=200)


@xray_recorder.capture("## Getting mix data")
def get_data(connection_thread: threading.ReturningThread) -> list[Mix]:
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    kce = "pk = :pkval"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": "mixes"},
        },
    )
    return [Mix(lens.focus(item, ["source", "S"])) for item in response["Items"]]
