from lib import web
from pytest import fixture, raises


@fixture
def boto3_mock(mocker):
    return mocker.patch("lib.web.boto3")


@fixture
def context(mocker):
    return mocker.Mock(name="context")


@fixture
def event():
    return {}


@fixture
def table_mock(boto3_mock, mocker):
    tbl_mock = boto3_mock.resource.return_value.Table = mocker.Mock(name="Table")
    return tbl_mock


def test_web(context, event, mocker, table_name):
    mocker.patch("lib.web.dispatch.Dispatcher.dispatch", return_value=True)
    assert web.handler(event, context)


def test_web_error(context, event, mocker, table_name):
    mocker.patch("lib.web.dispatch.Dispatcher.dispatch", side_effect=ValueError)
    expected = {
        "body": "<div>\nError: \n</div>",
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 400,
        "cookies": [],
    }
    observed = web.handler(event, context)
    assert observed == expected


def test_web_exception(context, event, mocker, table_name):
    mocker.patch("lib.web.dispatch.Dispatcher.dispatch", side_effect=Exception)
    expected = {
        "body": "<div>\nError: \n</div>",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    observed = web.handler(event, context)
    assert observed == expected


def test_web_no_table(context, event, mocker):
    mocker.patch(
        "lib.web.dispatch.Dispatcher.dispatch",
        side_effect=Exception("ddb_table_name env variable is not properly set"),
    )
    observed = web.handler(event, context)
    expected = {
        "body": "<div>\nError: ddb_table_name env variable is not properly set\n</div>",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    assert observed == expected


def test_ddb_connect(boto3_mock, table_name):
    boto3_mock.Session.return_value.client.return_value = "client"
    boto3_mock.Session.return_value.resource.return_value.Table.return_value = "table"
    observed = web.ddb_connect(table_name)
    expected = (table_name, "client", "table")
    assert observed == expected


def test_ddb_connect_no_table():
    with raises(Exception):
        web.ddb_connect(None)


def test_get_table_connection(connection_thread_mock, client_mock, mocker, resource_mock, table_name):
    mocker.patch("lib.web.os.environ", {"ddb_table_name": table_name})
    t = web.get_table_connection()
    expected = (table_name, client_mock, resource_mock)
    observed = t.join()
    assert observed == expected


def test_global_table_connection_holder(connection_thread_mock, context, event, mocker):
    mocker.patch("lib.web.table_connection_thread_global_holder", connection_thread_mock)
    mocker.patch("lib.web.dispatch.Dispatcher.dispatch", return_value=True)
    assert web.handler(event, context)
