from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from botocore.config import Config
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from typing import cast
import boto3
import logging
import os
import sys

from lib import (
    dispatch,
    return_,
    threading,
    types,
)

patch_all()

logging_level = os.environ.get("logging_level", "DEBUG").upper()
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging_level,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

SESSION_CONFIG = Config(retries={"max_attempts": 10, "mode": "standard"})


@xray_recorder.capture("## Establish DDB connection thread")
def ddb_connect(table_name: str | None) -> types.ConnectionThreadResultType:
    if not table_name:
        raise Exception("ddb_table_name env variable is not properly set")
    session = boto3.Session()
    client = cast(DynamoDBClient, session.client("dynamodb", config=SESSION_CONFIG))
    rsrc = cast(DynamoDBServiceResource, session.resource("dynamodb", config=SESSION_CONFIG))
    return cast(types.ConnectionThreadResultType, (table_name, client, rsrc.Table(table_name)))


@xray_recorder.capture("## Spawn table connection thread")
def get_table_connection() -> threading.ReturningThread:
    table_name = os.environ.get("ddb_table_name")
    table_connection_thread = threading.ReturningThread(target=ddb_connect, args=(table_name,), daemon=True)
    table_connection_thread.start_safe()
    return table_connection_thread


table_connection_thread_global_holder: threading.ReturningThread | None = None


@xray_recorder.capture("## Main handler")
def handler(event: dict, context):
    logger.debug(event)
    logger.debug(str(context))
    global table_connection_thread_global_holder
    if table_connection_thread_global_holder:
        table_connection_thread: threading.ReturningThread = table_connection_thread_global_holder
    else:
        table_connection_thread = get_table_connection()
        table_connection_thread_global_holder = table_connection_thread
    dispatcher = dispatch.Dispatcher(
        connection_thread=table_connection_thread,
        elements={
            "/session": "lib.session",
            "/banner": "lib.banner",
            "/images": "lib.image_carousel",
            "/logo": "lib.logo",
            "/mixes": "lib.mixes",
            "/contact": "lib.contact",
            "/sections": "lib.sections",
            "/sections/about": "lib.sections.about",
            "/sections/mixes": "lib.sections.mixes",
            "/sections/contact": "lib.sections.contact",
        },
        prefix="/ui",
    )
    try:
        return dispatcher.dispatch(event)
    except ValueError as ve:
        logger.exception(ve)
        table_connection_thread.join()
        return return_.error(ve, 400)
    except Exception as e:
        logger.exception(e)
        table_connection_thread.join()
        return return_.error(e, 500)
