from lib.sections import about
from pytest import fixture


@fixture
def body():
    return "It all started one pandemic day..."


def test_act(connection_thread_mock, session_data):
    assert about.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_build(body, client_mock, connection_thread_mock, session_data):
    client_mock.get_item.return_value = {"Item": {"text": {"S": body}}}
    assert about.build(connection_thread_mock, session_data)
