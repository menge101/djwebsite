from pytest import fixture
import os


# The following fixtures are used to mock threads, uncomment and revise if needed
# @fixture(autouse=True)
# def disable_thread_call_maybe(connection_thread_mock, mocker, request):
#     if "thread_test" not in request.keywords:
#         mocker.patch("lib.website.threading.ReturningThread", return_value=connection_thread_mock)
#
#
# @fixture(autouse=True)
# def boto3_mock(mocker):
#     return mocker.patch("lib.website.boto3")


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
        "translate": {"state": "closed"},
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
