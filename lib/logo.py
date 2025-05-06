from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Attribute, Class, ID
from basilico.elements import Div, Element, SVG
from lib import return_, session, threading
from typing import cast
import lens
import logging
import os

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


@xray_recorder.capture("## Element template act function")
def act(
    connection_thread: threading.ReturningThread, session_data: session.SessionData, params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    session_data = cast(session.SessionData, session_data.copy())
    logger.debug(f"session_data: {session_data}")
    logger.debug(f"params: {params}")
    # This guards against the edge case where an action is requested prior to the session being initialized
    if "id_" not in session_data or "sk" not in session_data:
        raise ValueError("Improperly formatted session data, likely stemming from session corruption")
    if not params:
        return session_data, []
    # logo element supports two actions
    # 1) Starting animation
    if params.get("action") == "start":
        session_data["logo"] = {"state": "rotate"}
    # 2) Stopping animation
    elif params.get("action") == "stop":
        session_data["logo"] = {"state": "still"}
    # If it's not one of those two, ignore it, build defaults to making it rotate when state is undefined
    else:
        logger.info(f"Unexpected parameter(s): {params}")
    session.update_session_thread(connection_thread, session_data, "logo")
    return session_data, []


@xray_recorder.capture("## Applying logo template")
def apply_template(rotating: bool) -> str:
    # the state here is used to set the state change behavior, so this is the action we want to offer to the ui
    # and it is a little backwards seeming, but on rotating, we want to offer stop
    # and on not rotating we want to offer start
    state = "stop" if rotating else "start"
    logger.debug(f"Rotating is {rotating} so we want ot offer the next state of {state}")
    template = Div(
        htmx.Get(f"/ui/logo?action={state}"),
        htmx.Swap("outerHTML"),
        htmx.Trigger("click"),
        Class("logo"),
        SVG(
            Class("block-centered w-full max-w-48"),
            Attribute("viewBox", "-2 -2 132 132"),
            Element(
                "defs",
                Element(
                    "mask",
                    ID("mask"),
                    Attribute("maskUnits", "userSpaceOnUse"),
                    Element(
                        "circle",
                        Class("logo-mask"),
                        Attribute("cx", "63.5"),
                        Attribute("cy", "63.5"),
                        Attribute("r", "63.5"),
                    ),
                ),
            ),
            Element(
                "g",
                Attribute("transform", "rotate(45 63.5 63.5)"),
                Class("rotating" if rotating else "not-rotating"),
                Element(
                    "path",
                    ID("red"),
                    Class("logo-stripe1"),
                    Attribute("d", "m0.50612 10.583v-10.077h125.99v20.154h-125.99z"),
                    Attribute("mask", "url(#mask)"),
                ),
                Element(
                    "path",
                    ID("orange"),
                    Class("logo-stripe2"),
                    Attribute("d", "m0.49969 31.749v-10.084h126v20.167h-126z"),
                    Attribute("mask", "url(#mask)"),
                ),
                Element(
                    "path",
                    ID("yellow"),
                    Class("logo-stripe3"),
                    Attribute("d", "m0.49968 52.916v-10.083h126v20.166h-126z"),
                    Attribute("mask", "url(#mask)"),
                ),
                Element(
                    "path",
                    ID("green"),
                    Class("logo-stripe4"),
                    Attribute("d", "m0.49968 74.083v-10.083h126v20.166h-126z"),
                    Attribute("mask", "url(#mask)"),
                ),
                Element(
                    "path",
                    ID("blue"),
                    Class("logo-stripe5"),
                    Attribute("d", "m0.49968 95.249v-10.083h126v20.166h-126z"),
                    Attribute("mask", "url(#mask)"),
                ),
                Element(
                    "path",
                    ID("purple"),
                    Class("logo-stripe6"),
                    Attribute("d", "m0.51281 116.41v-10.07h125.97v20.141h-125.97z"),
                    Attribute("mask", "url(#mask)"),
                ),
            ),
            Element(
                "circle",
                Attribute("cx", "64"),
                Attribute("cy", "64"),
                Attribute("r", "60"),
                ID("circlefill"),
                Class("fill-none stroke-base-content"),
            ),
            Element(
                "circle",
                ID("outercircle"),
                Class("outercircle stroke-base-200 fill-none"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "63.5"),
            ),
            Element(
                "circle",
                ID("innercircle"),
                Class("outercircle stroke-base-300 fill-none"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "57"),
            ),
            Element(
                "circle",
                ID("recordlabel"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "19.05"),
            ),
            Element(
                "circle",
                ID("spindlehole"),
                Class("fill-base-content"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "2.54"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "24"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "26"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "33"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "38"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "42"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "44"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "48"),
            ),
            Element(
                "circle",
                Class("vinyl-lines"),
                Attribute("cx", "63.5"),
                Attribute("cy", "63.5"),
                Attribute("r", "50"),
            ),
            Element(
                "path",
                ID("wzl-fill"),
                Class("fill-base-content"),
                Attribute(
                    "d",
                    "m97.609 44.547-0.21118 33.556c-1.01 0.12545-1.7461 0.52783-1.7461 1.0087 0 0.27144 0.23646 0.5173 0.62218 0.70332h-20.043c0.0053-0.02721 0.0083-0.05477 0.0083-0.08268 0-0.41002-0.58514-0.75082-1.372-0.83612l13.503-29.35c0.74275-0.34021 1.2439-0.99494 1.2439-1.7508v-1.6009c0-1.108-1.0765-1.9999-2.4133-1.9999h-18.452c-1.15 0-2.1051 0.66047-2.3502 1.5503-0.81844 0.13549-1.6151 0.7232-2.0691 1.6283l-13.882 27.676c-0.03257-0.04151-0.06386-0.08359-0.0987-0.12402l-5.6601-6.5696 0.24495-0.27647c0.91988-1.0383 0.91513-2.4274-0.01034-3.1145-0.92547-0.68715-2.4112-0.40419-3.3311 0.63407l-8.4005 9.4821-14.127-27.44c-0.056-0.10878-0.12214-0.20591-0.1881-0.30282v-1.0036h-1.4015c-0.21264-0.04252-0.42675-0.04253-0.63407 0h-10.431v2.9218h7.8357c0.03418 0.35043 0.12827 0.70903 0.30437 1.0511l16.097 31.267c0.59416 1.1541 1.7915 1.6587 2.6846 1.1312l1.2904-0.76223c0.85834-0.50694 1.1058-1.7759 0.59686-2.8985l6.9076-7.7975 5.5051 6.3888c0.36807 0.42717 0.80472 0.72115 1.2444 0.87488-0.18077 1.088 0.23706 2.1314 1.1286 2.5725l0.75138 0.37155c1.1466 0.56721 2.6244-0.08238 3.3135-1.4562l15.149-30.203h11.863l-12.983 28.22c-0.26242 0.57043-0.24704 1.2093-0.01447 1.7994h-0.82631v2.4123h53.117v-2.4123h-15.632c0.38572-0.18601 0.62218-0.43187 0.62218-0.70332 0-0.58178-1.0759-1.0501-2.4128-1.0501h-1.173l0.21118-33.515z",
                ),
            ),
            Element(
                "path",
                ID("wzl"),
                Class("stroke-base-100 fill-base-100"),
                Attribute(
                    "d",
                    "m103.32 42.025c-0.0955 0-0.188 0.01099-0.27853 0.02791-0.0694-0.0055-0.13996-0.0083-0.21136-0.0083h-4.9c-1.108 0-1.9999 0.67276-1.9999 1.5084 0 0.01107 7.22e-4 0.02206 1e-3 0.03307-0.04812 0.18935-0.08212 0.38605-0.0832 0.59428l-0.16843 32.549h-18.122l15.581-30.681c0.45193-0.8899 0.57954-1.7455 0.41083-2.3425-0.03619-0.80832-0.96884-1.4516-2.1255-1.4516h-23.673c-0.70238 0-1.3215 0.23784-1.7089 0.60513-0.37337 0.25683-0.70877 0.6244-0.93069 1.0738l-13.745 27.836-6.9076-8.3437c-0.30044-0.36294-0.69598-0.65538-1.1121-0.84904-0.08636-0.0684-0.18957-0.12458-0.31419-0.16175-0.10313-0.03076-0.21444-0.04739-0.33124-0.05271-0.32739-0.06621-0.64389-0.06417-0.91364 0.02377-0.23286 0.07591-0.40252 0.2069-0.51056 0.37362-0.39773 0.22118-0.77835 0.52323-1.0831 0.88367l-6.674 7.8925-13.393-27.425c-0.19722-0.40385-0.65222-0.65742-1.0971-0.64699-0.15161-0.04102-0.3154-0.06459-0.48731-0.06459h-7.1438c-0.76683 0-1.3839 0.44646-1.3839 1.0005v0.99994c0 0.554 0.61706 0.99994 1.3839 0.99994h6.6771l13.674 28c0.23587 0.483 0.84045 0.75639 1.3555 0.61288l0.92966-0.25942c0.23631-0.06585 0.40777-0.2098 0.5054-0.39067 0.28375-0.19371 0.55027-0.42705 0.77515-0.69298l7.075-8.3669 7.3696 8.9028c0.24041 0.29042 0.54261 0.53411 0.86661 0.71985 0.14011 0.22122 0.34913 0.3858 0.62373 0.46147 0.31529 0.08689 0.66644 0.04276 1.0077-0.0987 0.05959-0.01113 0.11774-0.02519 0.17363-0.04341 0.25551-0.08329 0.43601-0.23209 0.54105-0.42271 0.25571-0.23258 0.48254-0.51706 0.64596-0.84801l14.182-28.72h21.943l-15.529 30.58c-0.37819 0.7447-0.53086 1.4662-0.4718 2.0319-0.04689 0.11651-0.07441 0.23761-0.07441 0.36328 0 0.831 1.0871 1.5002 2.4376 1.5002h20.088c0.94939 0 1.767-0.3314 2.1699-0.81649 0.48985-0.36688 0.81271-1.0103 0.81649-1.7508l0.16381-32.1h2.4805l0.0863 32.959c0 0.51952 0.26154 0.97526 0.66042 1.2444 0.36539 0.30222 0.89173 0.49248 1.481 0.49248h14.002c1.108 0 1.9999-0.66917 1.9999-1.5002s-0.89187-1.4996-1.9999-1.4996h-12.644l-0.0904-33.232c-2e-3 -0.83123-0.66917-1.5002-1.5002-1.5002zm-32.152 6.3417c-0.18508 0-0.36374 0.01676-0.53537 0.04548-0.77872-0.06599-1.7259 0.54526-2.2071 1.4666l-16.479 31.549-7.3995-9.0274c-0.72309-0.88222-1.9446-1.3957-2.7388-1.1514-0.15541 0.04782-0.28168 0.12157-0.38034 0.21497-0.27393 0.08734-0.52573 0.23976-0.69453 0.44235l-8.2899 9.9487-16.127-31.832c-0.22855-0.45113-0.7727-0.73101-1.278-0.6842-0.08109-0.01598-0.16544-0.02532-0.25218-0.02532h-4.8979c-0.631 0-1.1389 0.44594-1.1389 0.99994v1.0005c0 0.554 0.50795 0.99994 1.1389 0.99994h4.2225l16.414 32.399c0.25428 0.5019 0.89964 0.79583 1.4469 0.65887l1.0118-0.25322c0.21869-0.05472 0.38463-0.17158 0.49248-0.32194 0.16691-0.08628 0.31755-0.19593 0.42943-0.33021l8.5395-10.25 7.7768 9.4878c0.28676 0.34987 0.65237 0.63995 1.0382 0.84956 0.13117 0.15397 0.30487 0.26968 0.52658 0.32349 0.14729 0.03575 0.30427 0.03479 0.46405 0.01757 0.25525 0.03535 0.49806 0.02595 0.71003-0.03927 0.34095-0.1049 0.5449-0.33263 0.61082-0.62735 0.23896-0.22514 0.45298-0.4917 0.61236-0.79685l16.753-32.075c0.07582 0.0053 0.15254 0.0083 0.23048 0.0083h9.2392l-16.146 31.439c-0.50618 0.98562-0.26418 1.9392 0.5426 2.1384 0.10484 0.02588 0.21403 0.03632 0.32556 0.03514 0.29346 0.12649 0.62964 0.20464 0.99374 0.20464h50.461c1.108 0 1.9999-0.66917 1.9999-1.5002s-0.89188-1.4996-1.9999-1.4996h-48.722l15.991-31.136c0.46319-0.90192 0.29788-1.7754-0.3514-2.0702-0.40244-0.3707-1.0489-0.61133-1.7834-0.61133z",
                ),
            ),
        ),
    )
    return template.string()


@xray_recorder.capture("## Building logo body")
def build(
    _connection_thread: threading.ReturningThread, session_data: dict[str, str], *_args, **_kwargs
) -> return_.Returnable:
    logger.debug("Starting logo build")
    rotating = lens.focus(session_data, ["logo", "state"], default_result="rotate") == "rotate"
    return return_.http(body=apply_template(rotating=rotating), status_code=200)
