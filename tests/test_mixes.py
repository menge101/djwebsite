from lib import mixes
from pytest import fixture


@fixture
def mix(source):
    return mixes.Mix(source)


@fixture
def source():
    return "https://player-widget.mixcloud.com/widget/iframe/?feed=%2Fmenge101%2Fallied%2F"


def test_render(mix):
    assert mix.render().string()


def test_act(connection_thread_mock, session_data):
    assert mixes.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_build(client_mock, connection_thread_mock, session_data, source):
    client_mock.query.return_value = {"Items": [{"source": {"S": "source"}}]}
    observed = mixes.build(connection_thread_mock)
    assert observed["statusCode"] == 200
