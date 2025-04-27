from aws_xray_sdk.core import xray_recorder
from basilico import attributes, elements, htmx
from lib import return_, session, threading, types
from typing import cast
import lens
import logging
import os
import secrets

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

STRING_PREFIX = "contact#form#"


@xray_recorder.capture("## Contact act function")
def act(
    connection_thread: threading.ReturningThread, session_data: session.SessionData, params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    logger.debug("Contact act function")
    logger.debug(session_data)
    logger.debug(params)
    if all(
        [
            key in params.keys()
            for key in ["date", "phone", "karaoke?", "name", "description", "location", "time", "email"]
        ]
    ):
        logger.debug("all keys for form submission")
        session_data["contact"] = {"form": "submitted"}
    if params.get("form") == "clear":
        logger.debug("clear form")
        session_data["contact"] = {"form": "clear"}
    csrf: str = generate_csrf_token()
    session_data["contact"] = {"csrf": csrf}
    session.update_session_thread(connection_thread, session_data, "contact")
    return session_data, []


@xray_recorder.capture("## Applying contact form template")
def apply_form_template(localized_strings: dict[str, str], csrf_token: str) -> str:
    submit_button_script = """on keyup from closest <form/> debounced at 150ms
            if (<[required]:invalid/>).length > 0
                add @disabled
                put 'Check All Fields' into me
                then exit
            end
            remove @disabled
            put 'Submit' into me
                        """
    template = elements.Form(
        htmx.Get("/ui/contact"),
        htmx.Trigger("submit"),
        htmx.Swap("outerHTML"),
        attributes.ID("booking"),
        elements.Div(
            attributes.Class("w-full row-span-2 justify-center flex m-auto space-y-3"),
            elements.FieldSet(
                attributes.Class(
                    "fieldset w-3/4 bg-base-200 border border-base-300 p-4 rounded-box "
                    "place-content-center grid grid-rows-1 grid-cols-3"
                ),
                elements.Legend(
                    attributes.Class("fieldset-legend"),
                    elements.Text(localized_strings.get("contact_details", "Contact Details")),
                ),
                elements.Div(
                    attributes.Class("row-start-1 row-end-1 col-start-1"),
                    elements.Label(
                        attributes.Class("fieldset-label"), elements.Text(localized_strings.get("name", "Name"))
                    ),
                    elements.Input(
                        attributes.Class("input validator"),
                        attributes.Type("text"),
                        attributes.Name("name"),
                        attributes.Required(),
                        attributes.Pattern("[a-zA-Z ]{2,}"),
                    ),
                ),
                elements.Div(
                    attributes.Class("row-start-1 col-start-2"),
                    elements.Label(
                        attributes.Class("fieldset-label"),
                        elements.Text(localized_strings.get("email", "Email")),
                    ),
                    elements.Label(
                        attributes.Class("input validator"),
                        elements.SVG(
                            attributes.Class("h-[1em] opacity-50"),
                            attributes.Attribute("viewBox", "0 0 24 24"),
                            elements.Element(
                                "g",
                                attributes.Attribute("stroke-linejoin", "round"),
                                attributes.Attribute("stroke-linecap", "round"),
                                attributes.Attribute("stroke-width", "2.5"),
                                attributes.Attribute("fill", "none"),
                                attributes.Attribute("stroke", "currentColor"),
                                elements.Element(
                                    "rect",
                                    attributes.Attribute("width", "20"),
                                    attributes.Attribute("height", "16"),
                                    attributes.Attribute("x", "2"),
                                    attributes.Attribute("y", "4"),
                                    attributes.Attribute("rx", "2"),
                                ),
                                elements.Element(
                                    "path", attributes.Attribute("d", "m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7")
                                ),
                            ),
                        ),
                        elements.Input(
                            attributes.Type("email"),
                            attributes.Placeholder("mail@site.com"),
                            attributes.Name("email"),
                            attributes.Required(),
                        ),
                    ),
                    elements.Div(
                        attributes.Class("validator-hint hidden"),
                        elements.Text(localized_strings.get("enter_email", "Enter valid email address")),
                    ),
                ),
                elements.Div(
                    attributes.Class("row-start-1 col-start-3"),
                    elements.Label(
                        attributes.Class("fieldset-label"),
                        elements.Text(localized_strings.get("phone", "Phone Number")),
                    ),
                    elements.Input(
                        attributes.Class("input validator"),
                        attributes.Type("text"),
                        attributes.Name("phone"),
                        attributes.Required(),
                        # Validation supports international dialing with +1-999
                        # spaces, dashes, or nothing separators between number groups
                        # also supports parentheses around area code
                        attributes.Pattern(r"[\)\d\-\s\+\(]{10,}"),
                    ),
                ),
            ),
        ),
        elements.Div(
            attributes.Class("w-full place-content-center m-auto p-4 rounded-box"),
            elements.FieldSet(
                attributes.Class(
                    "fieldset w-3/4 m-auto grid-cols-3 grid-rows-1 grid bg-base-200 border border-base-300"
                ),
                elements.Legend(
                    attributes.Class("fieldset-legend"),
                    elements.Text(localized_strings.get("event_details", "Event Details")),
                ),
                elements.Div(
                    attributes.Class("grid-col[1]"),
                    elements.Div(
                        attributes.Class("row[1]"),
                        elements.Label(
                            attributes.Class("fieldset-label"),
                            elements.Text(localized_strings.get("date", "Date")),
                        ),
                        elements.Input(
                            attributes.Type("date"),
                            attributes.Class("input validator"),
                            attributes.Name("date"),
                            attributes.Required(),
                            # No validator pattern because apparently html doesn't apply it to date type inputs
                        ),
                    ),
                    elements.Div(
                        attributes.Class("row-[2]"),
                        elements.Label(
                            attributes.Class("fieldset-label"),
                            elements.Text(localized_strings.get("time", "Time")),
                        ),
                        elements.Input(
                            attributes.Type("time"),
                            attributes.Class("input validator"),
                            attributes.Name("time"),
                            attributes.Required(),
                            # No validation pattern because input handles it
                        ),
                    ),
                    elements.Div(
                        attributes.Class("row-[3]"),
                        elements.Label(
                            attributes.Class("fieldset-label"),
                            elements.Text(localized_strings.get("duration", "Duration")),
                        ),
                        elements.Div(
                            attributes.Class("w-full max-w-xs"),
                            elements.Label(
                                attributes.Class("fieldset-label block"),
                                elements.Input(
                                    attributes.Type("range"),
                                    attributes.Min("0"),
                                    attributes.Max("8"),
                                    attributes.Value("1"),
                                    attributes.Class("range"),
                                    attributes.Step("1"),
                                    attributes.Required(),
                                ),
                                elements.Div(
                                    attributes.Class("flex justify-between px-2.5 mt-2 text-xs"),
                                    elements.Span(elements.Text("0")),
                                    elements.Span(elements.Text("2")),
                                    elements.Span(elements.Text("4")),
                                    elements.Span(elements.Text("6")),
                                    elements.Span(elements.Text("8+")),
                                ),
                            ),
                        ),
                    ),
                ),
                elements.Div(
                    attributes.Class("grid-col[2], col-span-2"),
                    elements.Div(
                        elements.Label(
                            attributes.Class("fieldset-label"),
                            elements.Text(localized_strings.get("location", "Location")),
                        ),
                        elements.Textarea(
                            attributes.Class("textarea h-18 validator"),
                            attributes.Name("location"),
                            attributes.Required(),
                            attributes.MinLength("3"),
                        ),
                    ),
                    elements.Label(
                        attributes.Class("fieldset-label"),
                        elements.Text(localized_strings.get("event_type", "What kind of event is this?")),
                    ),
                    elements.Textarea(
                        attributes.Class("textarea h-24 w-full validator"),
                        attributes.Name("description"),
                        attributes.Required(),
                        # Validation checks for seven or more characters
                        attributes.MinLength("7"),
                    ),
                    elements.FieldSet(
                        attributes.Class("fieldset w-64"),
                        elements.Legend(
                            attributes.Class("fieldset-label"),
                            elements.Text(localized_strings.get("karaoke", "Karaoke?")),
                        ),
                        elements.Label(
                            attributes.Class("fieldset-label pt-4"),
                            elements.Text(localized_strings.get("no", "No")),
                            elements.Input(
                                attributes.Type("checkbox"),
                                attributes.Checked(),
                                attributes.Class("toggle"),
                                attributes.Name("karaoke?"),
                            ),
                            elements.Text(localized_strings.get("yes", "Yes")),
                        ),
                    ),
                ),
                elements.Div(
                    attributes.Class("col-start-2 col-end-2 col-span-1 content-center m-auto align-top"),
                    elements.Button(
                        attributes.Type("submit"),
                        attributes.FormAttr("booking"),
                        attributes.Class("btn btn-soft btn-success"),
                        attributes.Attribute("_", submit_button_script),
                        attributes.Disabled(),
                        elements.Text(localized_strings.get("submit", "Submit")),
                    ),
                ),
                elements.Input(
                    attributes.Type("hidden"),
                    attributes.Value(csrf_token),
                ),
            ),
        ),
    )
    return template.string()


@xray_recorder.capture("## Applying contact refresh form template")
def apply_refresh_template(localized_strings: dict[str, str]) -> str:
    template = elements.Div(
        attributes.Class(
            "w-full row-span-2 justify-center flex m-auto space-y-3 h-64 cursor-pointer bg-base-200 border border-base-300"
        ),
        htmx.Trigger("click"),
        htmx.Get("/ui/contact?form=clear"),
        htmx.Swap("outerHTML"),
        attributes.ID("form-base"),
        elements.Button(
            attributes.Class("justify-center align-center m-auto text-white cursor-pointer"),
            elements.SVG(
                attributes.Attribute("viewBox", "0 0 128 128"),
                elements.Element(
                    "g",
                    attributes.ID("surface1"),
                    elements.Element(
                        "path",
                        attributes.Class("refresh"),
                        attributes.Attribute(
                            "d",
                            (
                                "M16.08,59.26A8,8,0,0,1,0,59.26a59,59,0,0,1,97.13-45V8a8,8,0,1,1,16.08,0V33.35a8,8,0,0"
                                ",1-8,8L80.82,43.62a8,8,0,1,1-1.44-15.95l8-.73A43,43,0,0,0,16.08,59.26Zm22.77,19.6a8,8"
                                ",0,0,1,1.44,16l-10.08.91A42.95,42.95,0,0,0,102,63.86a8,8,0,0,1,16.08,0A59,59,0,0,1,"
                                "22.3,110v4.18a8,8,0,0,1-16.08,0V89.14h0a8,8,0,0,1,7.29-8l25.31-2.3Z"
                            ),
                        ),
                    ),
                ),
            ),
            elements.Text(localized_strings.get("refresh", "Refresh")),
        ),
    )
    return template.string()


@xray_recorder.capture("## Building contact body")
def build(
    connection_thread: threading.ReturningThread, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting contact build")
    logger.debug(session_data)
    localization: str = session_data.get("local", "en")
    localized_strings: dict[str, str] = get_localized_strings(connection_thread, localization, STRING_PREFIX)
    if lens.focus(session_data, ["contact", "form"], default_result="clear") == "submitted":
        return return_.http(body=apply_refresh_template(localized_strings), status_code=200)
    return return_.http(body=apply_form_template(localized_strings), status_code=200)


@xray_recorder.capture("## Generating CSRF token")
def generate_csrf_token() -> str:
    return str(secrets.randbits(256))


@xray_recorder.capture("## Getting localized strings for contact")
def get_localized_strings(
    connection_thread: threading.ReturningThread, localization: str, prefix: str
) -> dict[str, str]:
    table_name, ddb_client, _ = cast(types.ConnectionThreadResultType, connection_thread.join())
    kce = "pk = :pkval AND begins_with ( sk, :skval )"
    response = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression=kce,
        ExpressionAttributeValues={
            ":pkval": {"S": localization},
            ":skval": {"S": prefix},
        },
    )
    return package_data(response["Items"], prefix=prefix)


@xray_recorder.capture("## Packaging localized strings for contact")
def package_data(response: dict[str, str], prefix: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in response:
        key = lens.focus(item, ["sk", "S"]).removeprefix(prefix)
        text = lens.focus(item, ["text", "S"])
        data[key] = text
    return data
