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
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 222,
    }
    assert observed == expected


def test_html(body, status_code):
    observed = return_.http(body, status_code, {"test": ["test"]}, ["yo=lo"])
    expected = {
        "body": "<div>yolo</div>",
        "multiValueHeaders": {"Content-Type": ["text/html"], "Set-Cookie": ["yo=lo"], "test": ["test"]},
        "statusCode": 222,
    }
    assert observed == expected
