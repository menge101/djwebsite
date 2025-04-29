from aws_xray_sdk.core import xray_recorder
from basilico import attributes, elements
from lib import return_, session, threading, types
from typing import cast, TextIO
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class AutoSpanText(elements.Text):
    @staticmethod
    def nl_to_spans(text: str) -> str:
        dedupe = text.replace("\n\n", "\n")
        splits = dedupe.split("\n")
        joined = "</span><span>".join(splits)
        bookended = f"<span>{joined}</span>"
        return bookended

    def render(self, w: TextIO):
        if self.to_render:
            escaped = elements.html.escape(self.text)
            stuff = self.nl_to_spans(escaped)
            w.write(stuff)


@xray_recorder.capture("## About act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying about template")
def apply_template(text: str) -> str:
    template = elements.Div(
        attributes.Class("hero bg-base-200 min-h-96 w-2/3 tab-content m-auto"),
        elements.Div(attributes.Class("hero-content text-center flex-col w-3/4"), AutoSpanText(text)),
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
