from aws_xray_sdk.core import xray_recorder
from basilico.attributes import Alt, Attribute, Class, ID, Href, Src
from basilico.elements import A, Div, Element, Img, SVG
from lib import return_, session, threading, types
from typing import cast
import lens
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Image:
    def __init__(self, url: str, alt_text: str):
        self.url = url
        self.alt_text = alt_text

    def render(self) -> Element:
        template = Div(
            ID(f"image{id(self)}"),
            Class("carousel-item w-full justify-center self-center"),
            Div(
                Class("w-auto"),
                Img(Src(self.url), Alt(self.alt_text), Class("object-cover")),
            ),
        )
        return template

    def render_indicator(self) -> Element:
        template = A(
            Href(f"#image{id(self)}"),
            SVG(
                Attribute("viewBox", "0 0 100 100"),
                Class("carousel-indicator btn btn-xs"),
                Element(
                    "ellipse",
                    Attribute("cx", "50"),
                    Attribute("cy", "50"),
                    Attribute("rx", "10"),
                    Attribute("ry", "10"),
                    Class("carousel-indicator"),
                ),
            ),
        )
        return template


@xray_recorder.capture("## Image Carousel act function")
def act(
    _connection_thread: threading.ReturningThread, session_data: session.SessionData, _params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    return session_data, []


@xray_recorder.capture("## Applying Image Carousel template")
def apply_template(images: list[Image]) -> str:
    template = Div(
        Class("w-auto mt-10 flex flex-col justify-center"),
        Div(
            Class("carousel bg-neutral rounded-box space-x-4 p-4 w-auto"),
            *(image.render() for image in images),
        ),
        Div(Class("flex w-full justify-center gap-2 py-2"), *(image.render_indicator() for image in images)),
    )
    return template.string()


@xray_recorder.capture("## Building Image Carousel body")
def build(connection_thread: threading.ReturningThread, *_args, **_kwargs) -> return_.Returnable:
    logger.debug("Starting image carousel build")
    images: list[Image] = get_data(connection_thread)
    return return_.http(body=apply_template(images), status_code=200)


@xray_recorder.capture("## Querying Images")
def get_data(connection_thread: threading.ReturningThread) -> list[Image]:
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    kce = "pk = :pkval"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": "images"},
        },
    )
    return package_data(response["Items"])


@xray_recorder.capture("## Packaging image data")
def package_data(data: dict[str, dict[str, str]]) -> list[Image]:
    return [Image(lens.focus(item, ["url", "S"]), lens.focus(item, ["alt_text", "S"])) for item in data]
