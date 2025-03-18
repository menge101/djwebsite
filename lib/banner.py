from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Class
from basilico.elements import Div, Text
from lib import return_, session, threading
from typing import Optional
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Banner act function")
def act(
    _connection_thread: threading.ReturningThread,
    session_data: session.SessionData,
    _params: dict[str, str],
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying banner template")
def apply_template(environment_name: Optional[str]) -> str:
    if environment_name:
        return Div(
            Class("banner"),
            Text(f"This is the {environment_name} environment"),
        ).string()
    return Div(Class("banner invisible"), Text("Environment name not set")).string()


@xray_recorder.capture("## Building banner body")
def build(*_args, **_kwargs) -> return_.Returnable:
    logger.debug("Starting banner build")
    environment_name = os.environ.get("environment_name")
    return return_.http(body=apply_template(environment_name), status_code=200)
