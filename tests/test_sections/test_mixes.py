from lib.sections import mixes


def test_act(connection_thread_mock, session_data):
    assert mixes.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_build(client_mock, connection_thread_mock, session_data):
    observed = mixes.build()
    expected = {
        "body": '<div class="tab-content not-prose justify-center flex flex-col m-auto w-full" hx-get="/ui/mixes" hx-trigger="load" hx-swap="innerHTML"></div>',
        "cookies": [],
        "headers": {"Content-Type": "text/html"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    assert observed == expected
