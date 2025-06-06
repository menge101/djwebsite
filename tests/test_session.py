from datetime import datetime, timezone
from pytest import fixture, raises
from lib import session


@fixture
def base_time():
    return datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0)


@fixture
def event_with_cookie(session_id):
    return {"headers": {"Cookie": f"id_={session_id}"}}


@fixture
def invalid_session_data():
    return {"yo": "lo"}


@fixture
def session_data_none():
    return {}


@fixture
def session_data(base_time, session_id):
    return {"id_": session_id, "ttl": base_time.timestamp()}


@fixture
def session_data_expired_timestamp(session_id):
    return {"id_": session_id, "sk": session_id, "pk": "session", "ttl": "69"}


def test_build_no_session(connection_thread_mock, mocker, session_data_none):
    mocker.patch("lib.session.cookie.expiration_time", return_value=0)
    mocker.patch("lib.session.cookie.expiration_as_ttl", return_value="0")
    mocker.patch("lib.session.uuid1", return_value="1")
    with raises(ValueError):
        session.build(connection_thread_mock, session_data_none)


def test_build_with_session(base_time, connection_thread_mock, mocker, session_id, session_data):
    mocker.patch("lib.session.cookie.expiration_as_ttl", return_value=base_time.timestamp())
    observed = session.build(connection_thread_mock, session_data)
    expected = {
        "body": "",
        "multiValueHeaders": {
            "Content-Type": ["text/html"],
            "Set-Cookie": ["id_=1234567890; Expires=Mon, 01 Jan 2024 00:00:00 GMT; HttpOnly; Secure; SameSite=Strict"],
        },
        "statusCode": 200,
    }
    assert observed == expected


def test_cookie_crumble(event_with_cookie, session_id):
    observed = session.get_session_id_from_cookies(event_with_cookie)
    expected = session_id
    assert observed == expected


def test_handle_session(connection_thread_mock, event_with_cookie, session_id, resource_mock, table_name):
    resource_mock.get_item.return_value = {"Item": {"id_": session_id, "ttl": "9999999999"}}
    observed = session.handle_session(event_with_cookie, connection_thread_mock)
    expected = {
        "id_": "1234567890",
        "ttl": str(int(datetime(2286, 11, 20, 17, 46, 39, tzinfo=timezone.utc).timestamp())),
    }
    assert observed == expected


def test_handle_session_expired_timestamp(
    connection_thread_mock, event_with_cookie, session_id, resource_mock, table_name
):
    resource_mock.get_item.return_value = {"Item": {"id_": session_id, "ttl": "9999"}}
    observed = session.handle_session(event_with_cookie, connection_thread_mock)
    expected = session.DEFAULT_SESSION_VALUES
    assert observed == expected


def test_handle_session_with_id_without_db_record(
    connection_thread_mock, event_with_cookie, session_id, resource_mock, table_name
):
    resource_mock.get_item.return_value = {}
    observed = session.handle_session(event_with_cookie, connection_thread_mock)
    expected = session.DEFAULT_SESSION_VALUES
    assert observed == expected


def test_act_no_session(connection_thread_mock, mocker, resource_mock, session_data_none):
    mocker.patch("lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0))
    mocker.patch("lib.session.uuid1", return_value="1")
    observed = session.act(connection_thread_mock, session_data_none, {})
    expected = (
        {
            "id_": "1",
            "pk": "session",
            "sk": "1",
            "translate": {"local": "en"},
            "ttl": "0",
        },
        ["session-created"],
    )
    resource_mock.put_item.assert_called()
    assert observed == expected


def test_act_with_session(
    connection_thread_mock,
    mocker,
    resource_mock,
    session_data,
):
    mocker.patch("lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0))
    mocker.patch("lib.session.uuid1", return_value="1")
    observed = session.act(connection_thread_mock, session_data, {})
    resource_mock.put_item.assert_not_called()
    assert observed == (session_data, ["session-found"])


def test_build_with_invalid_session(mocker, invalid_session_data):
    mocker.patch("lib.session.cookie.expiration_time", return_value=datetime.fromtimestamp(0))
    mocker.patch("lib.session.uuid1", return_value="1")
    with raises(ValueError):
        session.build(mocker.Mock(name="anything"), invalid_session_data, {})


def test_create_session_raises_client_error(connection_thread_mock, mocker, resource_mock, session_data):
    class MockException(Exception):
        pass

    mocker.patch("lib.session.botocore.exceptions.ClientError", MockException)
    resource_mock.put_item.side_effect = MockException()
    with raises(ValueError):
        session.create_session(connection_thread_mock, session_data)
