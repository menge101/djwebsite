from pytest import fixture
from lib.dispatch import Dispatcher


@fixture
def delete_event():
    return {
        "requestContext": {
            "http": {"method": "DELETE", "path": "/ui/element"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
        "version": "2.0",
    }


@fixture
def http_request_event():
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/ui/element",
        "rawQueryString": "",
        "headers": {
            "x-amz-content-sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "content-length": "0",
            "x-amzn-tls-version": "TLSv1.3",
            "x-amz-date": "20250113T085918Z",
            "x-forwarded-proto": "https",
            "x-amz-source-account": "779846793683",
            "x-forwarded-port": "443",
            "x-forwarded-for": "197.254.28.218",
            "x-amz-security-token": "IQoJb3JpZ2luX2VjEAEaCXVzLWVhc3QtMSJHMEUCIHpiDgHIZR48kZH6zLVyh2xKUh7FI",
            "via": "2.0 c2115407817bd859da50cd8a7221b418.cloudfront.net (CloudFront)",
            "x-amz-source-arn": "arn:aws:cloudfront::779846793683:distribution/E6EV5I0TSP4B3",
            "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
            "x-amzn-trace-id": "Self=1-6784d5e6-6e53f41b50b7bb583bd6e63b;Root=1-6784d5e6-128581cb1a25f58c",
            "host": "bxdsranrgc5bkf5ph5b66dfz5i0okagy.lambda-url.us-east-1.on.aws",
            "accept-encoding": "gzip,deflate",
            "x-amz-cf-id": "uD2VrFaF-Zy611ClLevG0NSdiY634FlQrA8W-9mkoAWw6vHANZ0h0w==",
            "user-agent": "Amazon CloudFront",
        },
        "requestContext": {
            "accountId": "856369053181",
            "apiId": "bxdsranrgc5bkf5ph5b66dfz5i0okagy",
            "authorizer": {
                "iam": {
                    "accessKey": "ASIA4OY4SXX6RBVEYONU",
                    "accountId": "856369053181",
                    "callerId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                    "cognitoIdentity": None,
                    "principalOrgId": None,
                    "userArn": "arn:aws:sts::856369053181:assumed-role/OriginAccessControlRole/OriginAccessSession",
                    "userId": "AROA4OY4SXX6VEIZRJRCJ:OriginAccessSession",
                }
            },
            "domainName": "bxdsranrgc5bkf5ph5b66dfz5i0okagy.lambda-url.us-east-1.on.aws",
            "domainPrefix": "bxdsranrgc5bkf5ph5b66dfz5i0okagy",
            "http": {
                "method": "GET",
                "path": "/ui/element",
                "protocol": "HTTP/1.1",
                "sourceIp": "130.176.36.140",
                "userAgent": "Amazon CloudFront",
            },
            "requestId": "ac6def0d-d269-44a6-8e0b-9cc27caf3c32",
            "routeKey": "$default",
            "stage": "$default",
            "time": "13/Jan/2025:08:59:18 +0000",
            "timeEpoch": 1736758758971,
        },
        "isBase64Encoded": False,
    }


@fixture
def post_event():
    return {
        "requestContext": {
            "http": {"method": "POST", "path": "/ui/element"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
        "version": "2.0",
    }


@fixture
def unsupported_event():
    return {
        "requestContext": {
            "http": {"method": "GET", "path": "/ui/unsupported"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
        "version": "2.0",
    }


@fixture
def prefix():
    return "/ui"


@fixture
def table_name():
    return "test-data-table"


@fixture
def mock_dispatchable(mocker):
    return_value = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    mock_module = mocker.Mock(name="mock_module")
    mock_module.act.side_effect = lambda _d_tbl, data, _params: (data, [])
    mock_module.build.side_effect = lambda *args: return_value
    return mock_module


@fixture
def mock_import(mocker, mock_dispatchable):
    return mocker.patch("lib.dispatch.importlib.import_module", return_value=mock_dispatchable)


def test_dispatcher(
    connection_thread_mock,
    http_request_event,
    table_name,
    mock_import,
    prefix,
    session_data,
):
    observed = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(http_request_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_post(connection_thread_mock, post_event, table_name, mock_import, prefix, session_data):
    observed = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(post_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_delete(connection_thread_mock, delete_event, table_name, mock_import, prefix, session_data):
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(delete_event)
    assert observed_response["statusCode"] == 405


def test_dispatch_unsupported_element(
    connection_thread_mock,
    unsupported_event,
    table_name,
    mock_import,
    prefix,
    session_data,
):
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(unsupported_event)
    assert observed_response["statusCode"] == 404


def test_dispatch_missing_path(connection_thread_mock, table_name, mock_import, prefix, session_data):
    event = {
        "requestContext": {"http": {"method": "GET"}, "requestId": "yolo"},
        "rawQueryString": "",
        "version": "2.0",
    }
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_version(connection_thread_mock, table_name, mock_import, prefix, session_data):
    event = {
        "requestContext": {
            "http": {"method": "GET", "path": "/ui/element"},
            "requestId": "yolo",
        },
        "rawQueryString": "",
    }
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_method(connection_thread_mock, table_name, mock_import, prefix, session_data):
    event = {
        "requestContext": {"http": {"path": "/ui/element"}, "requestId": "yolo"},
        "rawQueryString": "",
    }
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_request_id(connection_thread_mock, table_name, mock_import, prefix, session_data):
    event = {
        "requestContext": {
            "http": {"path": "/ui/element", "method": "GET"},
        },
        "rawQueryString": "",
    }
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_query_string(connection_thread_mock, mock_import, prefix, session_data):
    event = {
        "requestContext": {
            "http": {"path": "/ui/element", "method": "GET"},
            "requestId": "yolo",
        },
    }
    observed_response = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(event)
    assert observed_response["statusCode"] == 400


def test_no_expected_path(connection_thread_mock, mock_import, session_data):
    event = {
        "version": "2.0",
        "requestContext": {
            "http": {"path": "/element", "method": "GET"},
            "requestId": "yolo",
        },
    }
    observed = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
    ).dispatch(event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_event_triggers_events(
    connection_thread_mock,
    prefix,
    session_data,
    http_request_event,
    mock_dispatchable,
    mock_import,
):
    mock_dispatchable.act.side_effect = lambda _d_tbl, data, _params: (data, ["yolo"])
    observed = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
        prefix=prefix,
    ).dispatch(http_request_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html", "HX-Trigger": "yolo, "},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_act_raises_value_error(connection_thread_mock, mock_import, mock_dispatchable, session_data):
    event = {
        "version": "2.0",
        "requestContext": {
            "http": {"path": "/element", "method": "GET"},
            "requestId": "yolo",
        },
    }
    mock_dispatchable.act.side_effect = ValueError()
    expected = {
        "body": "<div>\nError: \n</div>",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 500,
    }
    observed = Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/element": "lib.element"},
    ).dispatch(event)
    assert observed == expected
