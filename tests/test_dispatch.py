from pytest import fixture
from lib.dispatch import Dispatcher


@fixture
def base_event():
    return {
        "headers": {"Cookie": "id_=64477043-4019-11f0-b7b4-03ca0bb0d828"},
        "path": "/api/banner",
        "requestContext": {
            "httpMethod": "GET",
            "requestId": "yolo",
        },
        "queryStringParameters": None,
    }


@fixture
def delete_event(base_event):
    base_event["path"] = "/ui/element"
    base_event["requestContext"]["httpMethod"] = "DELETE"
    return base_event


@fixture
def dispatcher(connection_thread_mock, prefix, resource_mock):
    resource_mock.get_item.return_value = {"Item": {"ttl": "9999999999999"}}
    return Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/banner": "lib.banner", "/sections": "lib.sections", "/sections/about": "lib.sections.about"},
        prefix=prefix,
    )


@fixture
def dispatcher_no_prefix(connection_thread_mock, resource_mock):
    resource_mock.get_item.return_value = {"Item": {"ttl": "9999999999999"}}
    return Dispatcher(
        connection_thread=connection_thread_mock,
        elements={"/api/banner": "lib.banner", "/sections": "lib.sections"},
    )


@fixture
def event_no_cookie(base_event):
    base_event["headers"].pop("Cookie")
    return base_event


@fixture
def http_request_event():
    return {
        "resource": "/api/{proxy+}",
        "path": "/api/banner",
        "httpMethod": "GET",
        "headers": {
            "Cache-Control": "no-cache",
            "Cookie": "id_=64477043-4019-11f0-b7b4-03ca0bb0d828",
            "Host": "scr7d0o9fc.execute-api.us-east-1.amazonaws.com",
            "hx-current-url": "https://d1fburh65qk66y.cloudfront.net/#image140279298414304",
            "hx-request": "true",
            "Pragma": "no-cache",
            "Referer": "https://d1fburh65qk66y.cloudfront.net/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Via": "2.0 838419e255a7994eff844a15e983d6fe.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "ndxTWotdiZ-heRGPwu8rHc6zjwZepPIhCTXPL7QZS-V-kj4tvGNQ6g==",
            "X-Amzn-Trace-Id": "Root=1-683e519b-3c94570b6caa6fde354bea04",
            "X-Forwarded-For": "2600:4041:3a4:1a00:adde:bd0c:465e:3dd9, 64.252.67.55",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
            "X-Origin-Auth": "my-shared-secret",
        },
        "multiValueHeaders": {
            "Cache-Control": ["no-cache"],
            "Cookie": ["id_=64477043-4019-11f0-b7b4-03ca0bb0d828"],
            "Host": ["scr7d0o9fc.execute-api.us-east-1.amazonaws.com"],
            "hx-current-url": ["https://d1fburh65qk66y.cloudfront.net/#image140279298414304"],
            "hx-request": ["true"],
            "Pragma": ["no-cache"],
            "Referer": ["https://d1fburh65qk66y.cloudfront.net/"],
            "User-Agent": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0"],
            "Via": ["2.0 838419e255a7994eff844a15e983d6fe.cloudfront.net (CloudFront)"],
            "X-Amz-Cf-Id": ["ndxTWotdiZ-heRGPwu8rHc6zjwZepPIhCTXPL7QZS-V-kj4tvGNQ6g=="],
            "X-Amzn-Trace-Id": ["Root=1-683e519b-3c94570b6caa6fde354bea04"],
            "X-Forwarded-For": ["2600:4041:3a4:1a00:adde:bd0c:465e:3dd9, 64.252.67.55"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
            "X-Origin-Auth": ["my-shared-secret"],
        },
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": {"proxy": "banner"},
        "stageVariables": None,
        "requestContext": {
            "resourceId": "tcyx9e",
            "resourcePath": "/api/{proxy+}",
            "httpMethod": "GET",
            "extendedRequestId": "LkGwWFiQoAMEkTA=",
            "requestTime": "03/Jun/2025:01:36:27 +0000",
            "path": "/api/api/banner",
            "accountId": "779846793683",
            "protocol": "HTTP/1.1",
            "stage": "api",
            "domainPrefix": "scr7d0o9fc",
            "requestTimeEpoch": 1748914587469,
            "requestId": "98579f67-c28b-4432-aac0-da283819cf17",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": "2600:4041:3a4:1a00:adde:bd0c:465e:3dd9",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0",
                "user": None,
            },
            "domainName": "scr7d0o9fc.execute-api.us-east-1.amazonaws.com",
            "deploymentId": "nus24q",
            "apiId": "scr7d0o9fc",
        },
        "body": None,
        "isBase64Encoded": False,
    }


@fixture
def post_event(base_event):
    base_event["requestContext"]["httpMethod"] = "POST"
    return base_event


@fixture
def section_event(base_event):
    base_event["requestContext"]["httpMethod"] = "POST"
    base_event["path"] = "/api/sections"
    return base_event


@fixture
def about_event(base_event):
    base_event["requestContext"]["httpMethod"] = "POST"
    base_event["path"] = "/api/sections/about"
    return base_event


@fixture
def unsupported_event(base_event):
    base_event["path"] = "/api/unsupported"
    return base_event


@fixture
def prefix():
    return "/api"


@fixture
def table_name():
    return "test-data-table"


@fixture
def mock_dispatchable(mocker, mock_response):
    mock_module = mocker.Mock(name="mock_module")
    mock_module.act.side_effect = lambda _d_tbl, data, _params: (data, [])
    mock_module.build.side_effect = lambda *args: mock_response
    return mock_module


@fixture
def mock_import(mocker, mock_dispatchable):
    return mocker.patch("lib.dispatch.importlib.import_module", return_value=mock_dispatchable)


@fixture
def mock_response():
    return {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }


def test_dispatcher(
    dispatcher,
    http_request_event,
):
    observed = dispatcher.dispatch(http_request_event)
    expected = {
        "body": '<div class="banner invisible">Environment name not set</div>',
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatcher_sections(client_mock, dispatcher, section_event):
    client_mock.query.return_value = {"Items": [{"pk": {"S": "section"}, "sk": {"S": "none"}, "name": {"S": "about"}}]}
    client_mock.get_item.return_value = {
        "Item": {"pk": {"S": "en"}, "sk": {"S": "section#label#about"}, "text": {"S": "About"}}
    }
    observed = dispatcher.dispatch(section_event)
    expected = {
        "body": '<div class="justify-center flex"><div class="tabs tab-border '
        'justify-center text-sm font-bold w-full"><input type="radio" '
        'name="tab_group" class="tab min-w-fit w-1/1 md:pl-30 lg:pl-50 '
        'md:pr-30 rg:pr-50" aria-label="About"><div class="tab-content"><div '
        'class="justify-center" hx-get="/api/sections/none" '
        'hx-trigger="revealed" hx-swap="innerHTML"></div></div></div></div>',
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatcher_about_section(client_mock, dispatcher, about_event):
    client_mock.query.return_value = {"Items": [{"pk": {"S": "section"}, "sk": {"S": "none"}, "name": {"S": "about"}}]}
    client_mock.get_item.return_value = {
        "Item": {"pk": {"S": "en"}, "sk": {"S": "section#body#about"}, "text": {"S": "About body text\n\nyolo"}}
    }
    observed = dispatcher.dispatch(about_event)
    expected = {
        "body": '<div class="hero bg-base-200 min-h-96 xl:w-2/3 md:w-3/4 w-full '
        'tab-content m-auto"><div class="hero-content text-center flex-col '
        'md:w-3/4 w-15/16"><span>About body '
        "text</span><span>yolo</span></div></div>",
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 200,
    }
    assert observed == expected


def test_no_prefix(dispatcher_no_prefix, http_request_event, mock_import):
    observed = dispatcher_no_prefix.dispatch(http_request_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_post(dispatcher, post_event, mock_import):
    observed = dispatcher.dispatch(post_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_delete(delete_event, dispatcher, mock_import):
    observed_response = dispatcher.dispatch(delete_event)
    assert observed_response["statusCode"] == 405


def test_dispatch_unsupported_element(
    dispatcher,
    unsupported_event,
):
    observed_response = dispatcher.dispatch(unsupported_event)
    assert observed_response["statusCode"] == 404


def test_dispatch_missing_path(base_event, dispatcher):
    base_event.pop("path")
    observed_response = dispatcher.dispatch(base_event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_method(base_event, dispatcher):
    base_event["requestContext"].pop("httpMethod")
    observed_response = dispatcher.dispatch(base_event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_request_id(base_event, dispatcher):
    base_event["requestContext"].pop("requestId")
    observed_response = dispatcher.dispatch(base_event)
    assert observed_response["statusCode"] == 400


def test_dispatch_missing_query_string(base_event, dispatcher):
    base_event.pop("queryStringParameters")
    observed_response = dispatcher.dispatch(base_event)
    assert observed_response["statusCode"] == 200


def test_no_expected_path(base_event, dispatcher, mock_import):
    observed = dispatcher.dispatch(base_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected


def test_dispatch_event_triggers_events(
    dispatcher,
    http_request_event,
    mock_dispatchable,
    mock_import,
    resource_mock,
):
    resource_mock.get_item.return_value = {"Item": {"ttl": "9999999999999"}}
    mock_dispatchable.act.side_effect = lambda _d_tbl, data, _params: (data, ["yolo"])
    observed = dispatcher.dispatch(http_request_event)
    expected = {
        "body": "yolo",
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "multiValueHeaders": {"HX-Trigger": ["yolo, "]},
        "statusCode": 200,
    }
    assert observed == expected


def test_act_raises_value_error(base_event, dispatcher, mock_dispatchable, mock_import):
    mock_dispatchable.act.side_effect = ValueError()
    expected = {
        "body": "<div>\nError: \n</div>",
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 500,
    }
    observed = dispatcher.dispatch(base_event)
    assert observed == expected


def test_dispatch_no_cookie(event_no_cookie, dispatcher, mock_dispatchable, mock_import, mock_response, resource_mock):
    observed = dispatcher.dispatch(event_no_cookie)
    expected = mock_response
    assert observed == expected
