from lib import logo
from pytest import fixture, raises


@fixture
def params_invalid():
    return {"action": "yolo"}


@fixture
def params_start():
    return {"action": "start"}


@fixture
def params_stop():
    return {"action": "stop"}


@fixture
def session_data(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "sk": session_id,
        "translate": {"state": "closed"},
        "logo": {"state": "rotate"},
    }


@fixture
def session_data_none(session_data):
    session_data.pop("sk")
    session_data.pop("id_")
    return session_data


@fixture
def session_data_logo_spinning(session_data):
    return session_data


@fixture
def session_data_logo_stoppped(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "sk": session_id,
        "translate": {"state": "closed"},
        "logo": {"state": "still"},
    }


@fixture
def session_data_no_logo(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "sk": session_id,
        "translate": {"state": "closed"},
    }


def test_act_invalid(connection_thread_mock, params_invalid, session_data, session_data_logo_stoppped):
    observed = logo.act(connection_thread_mock, session_data, params_invalid)
    expected = (session_data_logo_stoppped, [])
    assert observed == expected


def test_act_start(connection_thread_mock, params_start, session_data):
    observed = logo.act(connection_thread_mock, session_data, params_start)
    expected = (session_data, [])
    assert observed == expected


def test_act_start_when_stopped(
    connection_thread_mock, params_start, session_data_logo_stoppped, session_data_logo_spinning
):
    observed = logo.act(connection_thread_mock, session_data_logo_stoppped, params_start)
    expected = (session_data_logo_spinning, [])
    assert observed == expected


def test_act_stop_when_spinning(
    connection_thread_mock, params_stop, session_data_logo_spinning, session_data_logo_stoppped
):
    observed = logo.act(connection_thread_mock, session_data_logo_spinning, params_stop)
    expected = (session_data_logo_stoppped, [])
    assert observed == expected


def test_act_stop(connection_thread_mock, params_stop, session_data, session_data_logo_stoppped):
    observed = logo.act(connection_thread_mock, session_data, params_stop)
    expected = (session_data_logo_stoppped, [])
    assert observed == expected


def test_act_no_session(connection_thread_mock, session_data_none):
    with raises(ValueError):
        logo.act(connection_thread_mock, session_data_none, {})


def test_act_no_logo_state(connection_thread_mock, params_start, session_data, session_data_no_logo):
    observed = logo.act(connection_thread_mock, session_data_no_logo, params_start)
    expected = (session_data, [])
    assert observed == expected


def test_build(connection_thread_mock, session_data):
    observed = logo.build(connection_thread_mock, session_data)
    assert observed["statusCode"] == 200
