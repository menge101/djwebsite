from pytest import fixture
import os

from lib import toast


@fixture(autouse=True)
def disable_thread_call_maybe(connection_thread_mock, mocker, request):
    if "thread_test" not in request.keywords:
        mocker.patch("lib.web.threading.ReturningThread", return_value=connection_thread_mock)


@fixture(autouse=True)
def boto3_mock(mocker):
    return mocker.patch("lib.web.boto3")


@fixture
def client_mock(mocker):
    return mocker.Mock(name="client")


@fixture
def connection_thread_mock(client_mock, mocker, resource_mock, table_name):
    t = mocker.Mock(name="thread")
    t.join.return_value = table_name, client_mock, resource_mock
    return t


@fixture
def fake_data():
    return {
        "name": "Test Test",
        "city": "Townsville",
        "state": "St",
        "email": "person@server.yo",
        "github": "github.com/yolo",
    }


@fixture
def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@fixture
def session_data(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "sk": session_id,
        "pk": "session",
    }


@fixture
def session_id():
    return "1234567890"


@fixture
def resource_mock(mocker):
    return mocker.Mock(name="resource")


@fixture
def table_name():
    return "test_table"


@fixture
def toast_message():
    return "yolo"


@fixture
def toast_id():
    return "001"


@fixture
def toast_obj(session_id, toast_message, toast_id, toast_ttl):
    return toast.Toast(session_id, toast_message, toast_id=toast_id, ttl=toast_ttl, level="info")


@fixture
def toast_ttl():
    return 99999


@fixture
def toast_db_record(session_id, toast_message, toast_id, toast_ttl):
    return {
        "pk": {"S": f"{session_id}-toast"},
        "sk": {"S": toast_id},
        "message": {"S": toast_message},
        "ttl": {"N": str(toast_ttl)},
        "level": {"S": "INFO"},
    }
