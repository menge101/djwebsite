from abc import abstractmethod
from aws_xray_sdk.core import xray_recorder
from types import ModuleType
from typing import cast, Optional, Protocol
import importlib
import lens
import logging
import os


from lib import return_, session, threading


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Dispatchable(Protocol):
    @abstractmethod
    def act(
        self,
        connection_thread: threading.ReturningThread,
        session_data: session.SessionData,
        query_params: dict[str, str],
    ) -> tuple[session.SessionData, list[str]]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def build(
        self,
        connection_thread: threading.ReturningThread,
        session_data: session.SessionData,
    ) -> return_.Returnable:
        raise NotImplementedError  # pragma: no cover


class DispatchInfo:
    def __init__(self, event: dict, expected_path_prefix: Optional[str] = None):
        self.event = event
        self.method: str = lens.focus(event, ["requestContext", "http", "method"], default_result=False)
        try:
            self.path: str = self.remove_prefix(
                expected_path_prefix,
                lens.focus(event, ["requestContext", "http", "path"]),
            )
        except lens.FocusingError:
            self.path = None  # type: ignore
        self.request_id: str = lens.focus(event, ["requestContext", "requestId"], default_result=False)
        self.query_params = lens.focus(event, ["queryStringParameters"], default_result=dict())
        try:
            self.session_id: Optional[str] = session.get_session_id_from_cookies(event)
        except KeyError:
            self.session_id = None
        self.validate()

    @staticmethod
    def remove_prefix(expected_path_prefix: Optional[str], path: str) -> str:
        if expected_path_prefix:
            return path.replace(expected_path_prefix, "")
        return path

    def validate(self) -> None:
        errors = []
        if self.event.get("version") != "2.0":
            errors.append(f"Invalid version: {self.event.get('version')}, should be 2.0")
        if self.method is False:
            errors.append("Method field not found")
        if self.path is None:
            errors.append("Path field not found")
        if self.request_id is False:
            errors.append("RequestId field not found")
        if errors:
            raise ValueError(", ".join(errors))
        return


class Dispatcher:
    def __init__(
        self,
        connection_thread: threading.ReturningThread,
        elements: dict[str, str],
        prefix: Optional[str] = None,
    ):
        self.connection_thread = connection_thread
        self.elements: dict[str, str] = elements
        self.prefix: Optional[str] = prefix
        self.session_data: session.SessionData = session.SessionData({})
        self.valid_element: Optional[ModuleType] = None

    @xray_recorder.capture("## Triggered events being added to response")
    @staticmethod
    def add_triggered_events_to_response(
        response: return_.Returnable, triggered_events: list[str]
    ) -> return_.Returnable:
        if not triggered_events:
            return response
        existing_triggered_events: str = lens.focus(response, ["headers", "HX-Trigger"], default_result="")
        triggered_events.extend(map(lambda x: x.strip(), existing_triggered_events.split(",")))
        headers: dict = cast(dict, response["headers"])
        headers["HX-Trigger"] = ", ".join(triggered_events)
        return response

    @xray_recorder.capture("## Initializing dispatch")
    def dispatch(self, event: dict) -> return_.Returnable:
        try:
            info = DispatchInfo(event, self.prefix)
        except ValueError as ve:
            return return_.error(ve, 400)
        try:
            dispatchee = self.validate(info)
        except KeyError as ke:
            logger.exception(ke)
            logger.error("Unsupported element requested")
            return return_.error(ke, 404)
        except ValueError as ve:
            return return_.error(ve, 405)
        session_data = session.handle_session(event, self.connection_thread)
        try:
            session_data, triggered_events = dispatchee.act(self.connection_thread, session_data, info.query_params)
        except ValueError as ve:
            return return_.error(ve, 500)
        built = dispatchee.build(self.connection_thread, session_data)
        return self.add_triggered_events_to_response(built, triggered_events)

    @xray_recorder.capture("## Validating request")
    def validate(self, info: DispatchInfo) -> Dispatchable:
        ALLOWED_METHODS = ["GET", "POST"]
        if info.method not in ALLOWED_METHODS:
            raise ValueError(f"Method {info.method} is not supported, must be one of {' ,'.join(ALLOWED_METHODS)}")
        xray_recorder.begin_subsegment(f"importing {self.elements[info.path]}")
        module = importlib.import_module(self.elements[info.path])
        xray_recorder.end_subsegment()
        return cast(Dispatchable, module)
