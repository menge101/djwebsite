from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div
from lib import return_, session, threading
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Mixes section act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying mixes section template")
def apply_template() -> str:
    template = Div(
        Class("tab-content not-prose justify-center flex flex-col m-auto w-full"),
        htmx.Get("/api/mixes"),
        htmx.Trigger("load"),
        htmx.Swap("innerHTML"),
    )
    return template.string()


@xray_recorder.capture("## Building mixes section body")
def build(*_args) -> return_.Returnable:
    logger.debug("Starting mixes section build")
    return return_.http(body=apply_template(), status_code=200)
