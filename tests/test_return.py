from lib import return_
from pytest import fixture


@fixture
def body():
    return "<div>yolo</div>"


@fixture
def exception():
    return ValueError("testing")


@fixture
def status_code():
    return 222


def test_error(exception, status_code):
    observed = return_.error(exception, status_code)
    expected = {
        "body": "<div>\nError: testing\n</div>",
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html"},
        "cookies": [],
    }
    assert observed == expected


def test_html(body, status_code):
    observed = return_.http(body, status_code, {"test": "test"}, ["yo=lo"])
    expected = {
        "body": "<div>yolo</div>",
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html", "test": "test"},
        "cookies": ["yo=lo"],
    }
    assert observed == expected
