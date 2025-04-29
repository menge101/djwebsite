from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Aria, Checked, Class, Name, Type
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
    def __init__(
        self, name: str, localization: str, width_class: str, active: bool, ddb_client: DynamoDBClient, table_name: str
    ):
        self.name = name
        self.width_class = width_class
        self.active = active
        self.label = self.get_label(name, localization, ddb_client, table_name)

    @classmethod
    def build_sections(
        cls,
        sections: list[dict[str, bool | str]],
        localization: str,
        width_class: str,
        ddb_client: DynamoDBClient,
        table_name: str,
    ) -> list["Section"]:
        logger.debug(f"Building sections: {sections}")
        return [
            Section(
                cast(str, section["sk"]),
                localization,
                width_class,
                cast(bool, section.get("active", False)),
                ddb_client,
                table_name,
            )
            for section in sections
        ]

    @staticmethod
    def get_label(name: str, localization: str, ddb_client: DynamoDBClient, table_name: str) -> str:
        response = ddb_client.get_item(
            TableName=table_name,
            Key={"pk": {"S": localization}, "sk": {"S": f"section#label#{name}"}},
        )
        return lens.focus(response, ["Item", "text", "S"])

    def render_input(self) -> Input:
        children = [
            Type("radio"),
            Name("tab_group"),
            Class(f"tab min-w-fit {self.width_class}"),
            Aria("label", self.label),
        ]
        if self.active:
            children.append(Checked())
        return Input(*children)

    def render_content(self) -> Div:
        klass = "tab-content tab-active" if self.active else "tab-content"
        return Div(
            Class(klass),
            Div(
                Class("justify-center"),
                htmx.Get(f"/ui/sections/{self.name}"),
                htmx.Trigger("revealed"),
                htmx.Swap("innerHTML"),
            ),
        )


@xray_recorder.capture("## Element template act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying element template template")
def apply_template(elements: list[Element]) -> str:
    template = Div(
        Class("justify-center flex"),
        Div(Class("tabs tab-border justify-center gap-2 pb-3 text-sm font-bold w-full"), *elements),
    )
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
    sections_raw: list[dict[str, bool | str]] = get_sections(ddb_client, table_name)
    width_class = f"w-1/{len(sections_raw)}"
    sections: list[Section] = Section.build_sections(sections_raw, localization, width_class, ddb_client, table_name)
    return package_data(sections)


@xray_recorder.capture("## Getting section names")
def get_sections(ddb_client: DynamoDBClient, table_name: str) -> list[dict[str, str]]:
    kce = "pk = :pkval"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": "section"},
        },
    )
    sections = [types.ddb_to_dict(section) for section in response["Items"]]
    return sections


@xray_recorder.capture("## Packaging data")
def package_data(sections: list[Section]) -> list[Input | Div]:
    elements: list[Input | Div] = []
    for section in sections:
        elements.append(section.render_input())
        elements.append(section.render_content())
    return elements
