from lib import contact
from pytest import fixture


@fixture
def csrf_token():
    return "1A"


@fixture
def session_data_form_submitted(session_data):
    session_data["contact"] = {"form": "submitted"}
    return session_data


@fixture
def session_data_with_csrf(csrf_token, session_data):
    session_data["contact"] = {"csrf": csrf_token}
    return session_data


def test_act_empty_params(connection_thread_mock, session_data):
    assert contact.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_act_clear_params(connection_thread_mock, session_data):
    params = {"form": "clear"}
    assert contact.act(connection_thread_mock, session_data, params) == (session_data, [])


def test_act_not_all_params(connection_thread_mock, session_data):
    params = {"name": "yolo"}
    assert contact.act(connection_thread_mock, session_data, params) == (session_data, [])


def test_act_all_params(connection_thread_mock, csrf_token, session_data_with_csrf):
    params = {
        "date": "030303",
        "phone": "2134567890",
        "karaoke?": "off",
        "name": "yolo",
        "description": "descript",
        "location": "yo",
        "time": "03:03AM",
        "email": "a@b.c",
        "csrf": csrf_token,
    }
    observed, _ = contact.act(connection_thread_mock, session_data_with_csrf, params)
    assert observed["contact"]["form"] == "submitted"


def test_act_no_csrf(connection_thread_mock, csrf_token, session_data):
    params = {
        "date": "030303",
        "phone": "2134567890",
        "karaoke?": "off",
        "name": "yolo",
        "description": "descript",
        "location": "yo",
        "time": "03:03AM",
        "email": "a@b.c",
        "csrf": csrf_token,
    }
    observed, _ = contact.act(connection_thread_mock, session_data, params)
    assert "form" not in observed["contact"]
    assert "csrf" in observed["contact"]


def test_build(client_mock, connection_thread_mock, session_data_with_csrf):
    client_mock.query.return_value = {
        "Items": [{"pk": {"S": "en"}, "sk": {"S": "contact#form#email"}, "text": {"S": "yolo"}}]
    }
    observed = contact.build(connection_thread_mock, session_data_with_csrf, {})
    expected = 200
    assert observed["statusCode"] == expected
    assert "yolo" in observed["body"]


def test_build_submitted(client_mock, connection_thread_mock, session_data_form_submitted):
    client_mock.query.return_value = {
        "Items": [{"pk": {"S": "en"}, "sk": {"S": "contact#form#refresh"}, "text": {"S": "yolo"}}]
    }
    observed = contact.build(connection_thread_mock, session_data_form_submitted, {})
    expected = 200
    assert observed["statusCode"] == expected
    assert "yolo" in observed["body"]
