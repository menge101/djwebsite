from lib import session
from pytest import fixture
import boto3


@fixture
def connection_thread_mock(mocker, table_name):
    client = boto3.client("dynamodb")
    resource = boto3.resource("dynamodb")
    thread_mock = mocker.Mock(name="ConnectionThread")
    thread_mock.join.return_value = table_name, client, resource
    return thread_mock


@fixture
def session_data(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "pk": "session",
        "sk": session_id,
        "logo": {"state": "rotate"},
    }


def test_update_session(connection_thread_mock, session_data, table):
    result = session.update_session(connection_thread_mock, session_data, "logo")
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
