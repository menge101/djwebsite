from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class
from basilico.elements import Div
from lib import return_, session, threading, toast
from typing import cast
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Element template act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying element template template")
def apply_template(toasts: list[toast.Toast]) -> str:
    template = Div(
        htmx.Swap("outerHTML"),
        htmx.Trigger("every 5s"),
        htmx.Get("/api/toaster"),
        Class("toast"),
        *(toast.render() for toast in toasts),
    )
    return template.string()


@xray_recorder.capture("## Building element template body")
def build(
    connection_thread: threading.ReturningThread, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting toaster build")
    # table_name, ddb_client, ddb_resource = connection_thread.join()
    session_id: str = cast(str, session_data["id_"])
    toasts: list[toast.Toast] = toast.query(connection_thread, session_id=session_id)
    body = apply_template(toasts=toasts)
    toast.destroy(connection_thread, toasts)
    return return_.http(body=body, status_code=200)
