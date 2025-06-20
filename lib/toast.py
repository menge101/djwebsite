from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Attribute, Class
from basilico.elements import Div, Element, Span, Text
from datetime import datetime, timedelta, UTC
from lib import threading, types
from typing import Any, cast, Optional
from uuid import uuid1
import logging
import os

DEFAULT_EXPIRATION_SECONDS = 60 * 10  # 600 seconds / 10 minutes

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Toast:
    def __init__(
        self,
        session_id: str,
        message: str,
        toast_id: Optional[str] = None,
        ttl: Optional[int] = None,
        level: Optional[str] = None,
    ):
        self.session_id = session_id
        self.toast_id = toast_id or str(uuid1())
        self.message = message
        self.ttl: int = ttl or int(self.expiration())
        self.level = (level or "NONE").upper()

    @xray_recorder.capture("## Toast#delete method")
    def delete(self, connection_thread: threading.ReturningThread):
        table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
        response = ddb_client.delete_item(TableName=table_name, Key=types.dict_to_ddb(self.key()))
        logger.debug("LOGGING toast delete response")
        logger.debug(response)
        return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @xray_recorder.capture("## Toast#key method")
    def key(self) -> dict[str, str]:
        return {"pk": f"{self.session_id}-toast", "sk": self.toast_id}

    @xray_recorder.capture("## Toast#marshal method")
    def marshal(self) -> dict[str, dict[str, int | str]]:
        key = self.key()
        key.update({"message": self.message, "ttl": self.ttl, "level": self.level})
        return types.dict_to_ddb(key)

    @xray_recorder.capture("## Toast#persist method")
    def persist(self, connection_thread: threading.ReturningThread) -> bool:
        db_item = self.marshal()
        table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
        response = ddb_client.put_item(TableName=table_name, Item=db_item)
        return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @xray_recorder.capture("## Toast#render method")
    def render(self) -> Element:
        alert_class = "alert"
        if self.level == "INFO":
            alert_class += " alert-info"
        elif self.level == "WARNING":
            alert_class += " alert-warning"
        elif self.level == "ERROR":
            alert_class += " alert-error"
        elif self.level == "SUCCESS":
            alert_class += " alert-success"
        return Div(
            Class(alert_class),
            Attribute(name="_", value="on click remove me"),
            Span(
                Text(self.message),
            ),
        )

    def __eq__(self, other) -> Any:
        if type(self) is not type(other):
            return False
        if self.session_id != other.session_id:
            return False
        if self.toast_id != other.toast_id:
            return False
        if self.message != other.message:
            return False
        if self.ttl != other.ttl:
            return False
        return True

    @classmethod
    @xray_recorder.capture("## toast unmarshal class method")
    def unmarshal(cls, obj: dict[str, dict[str, int | str]]) -> "Toast":
        unmarshalled_obj: dict[str, int | str] = types.ddb_to_dict(obj)
        return Toast(
            session_id=cast(str, unmarshalled_obj["pk"]).replace("-toast", ""),
            toast_id=cast(str, unmarshalled_obj["sk"]),
            message=cast(str, unmarshalled_obj["message"]),
            ttl=cast(int, unmarshalled_obj["ttl"]),
            level=cast(str, unmarshalled_obj["level"]),
        )

    @staticmethod
    @xray_recorder.capture("## toast expiration static method")
    def expiration(seconds: Optional[int] = None) -> int:
        seconds = seconds or DEFAULT_EXPIRATION_SECONDS
        time = datetime.now(UTC) + timedelta(seconds=seconds)
        return int(time.timestamp())


@xray_recorder.capture("## toast create function")
def create(
    connection_thread: threading.ReturningThread, session_id: str, message: str, level: Optional[str] = None
) -> str:
    """

    :param connection_thread: The connection thread object
    :param session_id: ID to associate this toast with
    :param message: Message body of toast
    :param level: Optional arg, defaults to "NONE", other valid options are "INFO", "WARNING", "ERROR", and "SUCCESS"
    :return: Returns the toast id
    """
    toast = Toast(session_id, message, level=level)
    toast.persist(connection_thread)
    return toast.toast_id


@xray_recorder.capture("## toast destroy function")
def destroy(connection_thread: threading.ReturningThread, toasts: list[Toast]) -> bool:
    return all([toast.delete(connection_thread) for toast in toasts])


@xray_recorder.capture("## toast get function")
def get(connection_thread: threading.ReturningThread, session_id: str, toast_id: str) -> Toast:
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    key_obj = {"pk": f"{session_id}-toast", "sk": toast_id}
    response = ddb_client.get_item(
        Key=key_obj,
        TableName=table_name,
    )
    return cast(Toast, Toast.unmarshal(response["Item"]))


@xray_recorder.capture("## toast query function")
def query(connection_thread: threading.ReturningThread, session_id: str) -> list[Toast]:
    logger.debug(f"Querying for toasts with session {session_id}, which will be modified to {session_id}-toast")
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    kce = "pk = :pkval"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": f"{session_id}-toast"},
        },
    )
    return [Toast.unmarshal(toast_record) for toast_record in response["Items"]]
