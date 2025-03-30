from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Aria, Class, Type
from basilico.elements import Div, Element, Input
from lib import return_, session, threading, types
from mypy_boto3_dynamodb.client import DynamoDBClient
from typing import cast
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Section:
    def __init__(self, name: str, localization: str, width_class: str, ddb_client: DynamoDBClient, table_name: str):
        self.name = name
        self.width_class = width_class
        self.label = self.get_label(name, localization, ddb_client, table_name)

    @staticmethod
    def get_label(name: str, localization: str, ddb_client: DynamoDBClient, table_name: str) -> str:
        response = ddb_client.get_item(
            TableName=table_name,
            Key={"pk": {"S": localization}, "sk": {"S": f"section#label#{name}"}},
        )
        return lens.focus(response, ["Item", "text", "S"])

    def render_input(self) -> Input:
        return Input(Type("radio"), Class(f"tab {self.width_class}"), Aria("label", self.label))

    def render_content(self) -> Div:
        return Div(
            Class("tab-content"),
            htmx.Get(f"/ui/sections/{self.name}"),
            htmx.Trigger("load"),
            htmx.Swap("outerHTML"),
        )


@xray_recorder.capture("## Element template act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying element template template")
def apply_template(elements: list[Element]) -> str:
    template = Div(Class("tabs tab-border flex-col justify-center"), *elements)
    return template.string()


@xray_recorder.capture("## Building section template body")
def build(
    connection_thread: threading.ReturningThread, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting Sections build")
    localization: str = session_data.get("local", "en")
    elements: list[Input | Div] = get_data(connection_thread, localization)
    return return_.http(body=apply_template(elements), status_code=200)


@xray_recorder.capture("## Getting section data")
def get_data(connection_thread: threading.ReturningThread, localization: str) -> list[Input | Div]:
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    section_names: list[str] = get_section_names(ddb_client, table_name)
    width_class = f"w-1/{len(section_names)}"
    sections: list[Section] = [
        Section(name, localization, width_class, ddb_client, table_name) for name in section_names
    ]
    return package_data(sections)


@xray_recorder.capture("## Getting section names")
def get_section_names(ddb_client: DynamoDBClient, table_name: str) -> list[str]:
    kce = "pk = :pkval"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": "section"},
        },
    )
    return lens.focus(response, ["Items", "name", "S"])


@xray_recorder.capture("## Packaging data")
def package_data(sections: list[Section]) -> list[Input | Div]:
    elements: list[Input | Div] = []
    for section in sections:
        elements.append(section.render_input())
        elements.append(section.render_content())
    return elements
