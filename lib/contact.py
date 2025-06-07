from aws_xray_sdk.core import xray_recorder
from basilico import attributes, elements, htmx
from datetime import datetime
from lib import return_, security, session, threading, types
from lib.threading import ReturningThread
from mypy_boto3_sns.client import SNSClient
from typing import cast
from urllib.parse import unquote
import boto3
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

STRING_PREFIX = "contact#form#"

sns_client_global_holder: ReturningThread | None = None


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
            for key in [
                "date",
                "phone",
                "karaoke?",
                "name",
                "description",
                "location",
                "time",
                "email",
                "duration",
                "csrf",
            ]
        ]
    ):
        logger.debug("all keys for form submission are filled")
        params = security.clean_data(params)
        try:
            if params["csrf"] == lens.focus(session_data, ["contact", "csrf"]):
                sns_connection_thread = get_sns_connection_thread()
                lens.carve(session_data, ["contact", "form"], "submitted")
                notification_message = format_notification(params)
                topic_arn = os.environ["notification_topic_arn"]
                sns_client: SNSClient = sns_connection_thread.join()
                sns_client.publish(
                    TopicArn=topic_arn,
                    Subject="Contact query received",
                    Message=notification_message,
                )
        except lens.FocusingError:
            logger.warning(f"Attempt to check CSRF without CSRF present in session: {session_data}")
    if params.get("form") == "clear":
        logger.debug("clear form")
        lens.carve(session_data, ["contact", "form"], "clear")
    lens.carve(session_data, ["contact", "csrf"], security.generate_csrf_token())
    session.update_session_thread(connection_thread, session_data, "contact")
    return session_data, []


@xray_recorder.capture("## Applying contact form template")
def apply_form_template(localized_strings: dict[str, str], session_data: session.SessionData) -> str:
    csrf_token = lens.focus(session_data, ["contact", "csrf"])
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
        htmx.Get("/api/contact"),
        htmx.Trigger("submit"),
        htmx.Swap("outerHTML"),
        attributes.ID("booking"),
        elements.Div(
            attributes.Class("justify-center flex-row flex flex-wrap space-y-3 md:p-4 w-full m-auto"),
            elements.FieldSet(
                attributes.Class(
                    "fieldset md:p-4 bg-base-200 border border-base-300 p-4 rounded-box place-content-center flex flex-col lg:flex-row lg:space-x-4 justify-center m-auto w-full"
                ),
                elements.Legend(
                    attributes.Class("fieldset-legend"),
                    elements.Text(localized_strings.get("contact_details", "Contact Details")),
                ),
                elements.Div(
                    attributes.Class("w-2/3 lg:w-1/4 min-w-60 max-lg:m-auto"),
                    elements.Label(
                        attributes.Class("fieldset-label"), elements.Text(localized_strings.get("name", "Name"))
                    ),
                    elements.Input(
                        attributes.Class("input validator w-full"),
                        attributes.Type("text"),
                        attributes.Name("name"),
                        attributes.Required(),
                        attributes.Pattern("[a-zA-Z ]{2,}"),
                    ),
                ),
                elements.Div(
                    attributes.Class("w-2/3 lg:w-1/4 min-w-60 max-lg:m-auto"),
                    elements.Label(
                        attributes.Class("fieldset-label"),
                        elements.Text(localized_strings.get("email", "Email")),
                    ),
                    elements.Label(
                        attributes.Class("input validator w-full"),
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
                            attributes.Class("fbc-has-badge fbc-UID_1 w-full"),
                        ),
                    ),
                    elements.Div(
                        attributes.Class("validator-hint hidden"),
                        elements.Text(localized_strings.get("enter_email", "Enter valid email address")),
                    ),
                ),
                elements.Div(
                    attributes.Class("w-2/3 lg:w-1/4 min-w-60 max-lg:m-auto"),
                    elements.Label(
                        attributes.Class("fieldset-label"),
                        elements.Text(localized_strings.get("phone", "Phone Number")),
                    ),
                    elements.Input(
                        attributes.Class("input validator w-full"),
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
            attributes.Class("w-full justify-center place-content-center m-auto lg:p-4 rounded-box flex flex-wrap"),
            elements.FieldSet(
                attributes.Class(
                    "fieldset w-full px-3 m-auto bg-base-200 border border-base-300 flex flex-col content-center"
                ),
                elements.Legend(
                    attributes.Class("fieldset-legend"),
                    elements.Text(localized_strings.get("event_details", "Event Details")),
                ),
                elements.Div(
                    attributes.Class(
                        "flex flex-col lg:flex-row justify-center w-full m-auto content-start items-start justify-center lg:space-x-4"
                    ),
                    elements.Div(
                        attributes.Class("flex flex-col w-full lg:w-4/12 min-w-45 justify-center max-lg:m-auto"),
                        elements.FieldSet(
                            attributes.Class("fieldset w-full min-w-40"),
                            elements.Label(
                                attributes.Class("fieldset-label"),
                                elements.Text(localized_strings.get("date", "Date")),
                            ),
                            elements.Input(
                                attributes.Type("date"),
                                attributes.Class("input validator w-full"),
                                attributes.Name("date"),
                                attributes.Required(),
                                # No validator pattern because apparently html doesn't apply it to date type inputs
                            ),
                        ),
                        elements.FieldSet(
                            attributes.Class("fieldset w-full min-w-40"),
                            elements.Label(
                                attributes.Class("fieldset-label"),
                                elements.Text(localized_strings.get("time", "Time")),
                            ),
                            elements.Input(
                                attributes.Type("time"),
                                attributes.Class("input validator w-full"),
                                attributes.Name("time"),
                                attributes.Required(),
                                # No validation pattern because input handles it
                            ),
                        ),
                        elements.FieldSet(
                            attributes.Class("fieldset w-full min-w-40"),
                            elements.Label(
                                attributes.Class("fieldset-label"),
                                elements.Text(localized_strings.get("duration", "Duration")),
                            ),
                            elements.Div(
                                attributes.Class("w-full lg:max-w-xs"),
                                elements.Label(
                                    attributes.Class("fieldset-label block"),
                                    elements.Input(
                                        attributes.Type("range"),
                                        attributes.Name("duration"),
                                        attributes.Min("0"),
                                        attributes.Max("8"),
                                        attributes.Value("1"),
                                        attributes.Class("range w-full"),
                                        attributes.Step("1"),
                                        attributes.Required(),
                                    ),
                                    elements.Div(
                                        attributes.Class("flex justify-between px-2.5 mt-2 text-xs w-full"),
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
                        attributes.Class("w-full lg:w-5/12 grow flex flex-col"),
                        elements.FieldSet(
                            attributes.Class("fieldset mb-2"),
                            elements.Label(
                                attributes.Class("fieldset-label"),
                                elements.Text(localized_strings.get("location", "Location")),
                            ),
                            elements.Textarea(
                                attributes.Class("textarea h-18 validator w-full md:w-1/4 min-w-75"),
                                attributes.Name("location"),
                                attributes.Required(),
                                attributes.MinLength("3"),
                            ),
                        ),
                        elements.FieldSet(
                            attributes.Class("fieldset mb-2 mt-2"),
                            elements.Label(
                                attributes.Class("fieldset-label"),
                                elements.Text(localized_strings.get("event_type", "What kind of event is this?")),
                            ),
                            elements.Textarea(
                                attributes.Class("textarea h-24 w-full min-w-75 validator"),
                                attributes.Name("description"),
                            ),
                        ),
                        elements.FieldSet(
                            attributes.Class("fieldset w-full lg:w-1/2 mt-2"),
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
                ),
                elements.Div(
                    attributes.Class("flex justify-center"),
                    elements.Div(
                        attributes.Class("justify-center w-full lg:w-2/3 flex"),
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
                        attributes.Name("csrf"),
                        attributes.Value(csrf_token),
                    ),
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
        htmx.Get("/api/contact?form=clear"),
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
    connection_thread: threading.ReturningThread, session_data: session.SessionData, *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting contact build")
    logger.debug(session_data)
    localization: str = cast(str, session_data.get("local", "en"))
    localized_strings: dict[str, str] = get_localized_strings(connection_thread, localization, STRING_PREFIX)
    if lens.focus(session_data, ["contact", "form"], default_result="clear") == "submitted":
        return return_.http(body=apply_refresh_template(localized_strings), status_code=200)
    return return_.http(body=apply_form_template(localized_strings, session_data), status_code=200)


@xray_recorder.capture("## Formatting notification message")
def format_notification(params: dict[str, str]) -> str:
    params.pop("csrf")
    params["name"] = params["name"].replace("%20", " ")
    params["email"] = params["email"].replace("%40", "@")
    params["location"] = params["location"].replace("%20", " ")
    params["description"] = params["description"].replace("%20", " ")
    params["date"] = datetime.strptime(params["date"], "%Y-%m-%d").strftime("%a %b %d %Y")
    params["karaoke?"] = "yes" if params["karaoke?"] == "on" else "no"
    params["time"] = datetime.strptime(unquote(params["time"]), "%H:%M").strftime("%I:%M %p")
    return (
        f"{params['name']} - {params['phone']} - {params['email']}\n"
        f"{params['date']} - {params['time']} for {params['duration']} hours\n"
        f"Location: {params['location']}\n"
        f"Description: {params['description']}\n"
        f"Karaoke?: {params['karaoke?']}\n"
    )


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


@xray_recorder.capture("## Create SNS client")
def create_sns_client() -> SNSClient:
    return boto3.client("sns")


@xray_recorder.capture("## Bring SNS client into process")
def get_sns_connection_thread() -> ReturningThread:
    global sns_client_global_holder
    if sns_client_global_holder:
        sns_client_thread: ReturningThread = sns_client_global_holder
    else:
        sns_client_thread = get_sns_connection()
        sns_client_global_holder = sns_client_thread
    return sns_client_thread


@xray_recorder.capture("## Spawn SNS connection thread")
def get_sns_connection() -> ReturningThread:
    sns_client_thread = threading.ReturningThread(target=create_sns_client, daemon=True)
    sns_client_thread.start_safe()
    return sns_client_thread
