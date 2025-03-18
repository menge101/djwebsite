from lib import log


def test_handler(mocker):
    observed = log.handler({}, mocker.Mock())
    expected = {
        "statusCode": 200,
        "body": "<div>htmx loaded</div>",
        "headers": {"Content-Type": "text/html"},
    }
    assert observed == expected
