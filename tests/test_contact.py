from lib import contact
from pytest import fixture


@fixture
def csrf_token():
    return "1A"


@fixture
def disable_thread_call_maybe(connection_thread_mock, mocker, request, sns_connection_thread_mock):
    mocker.patch("lib.web.threading.ReturningThread", return_value=sns_connection_thread_mock)


@fixture
def env_with_notification_arn(mocker):
    mocker.patch("os.environ", {"notification_topic_arn": "arn:aws:notification"})


@fixture
def form_params(csrf_token):
    return {
        "date": "0003-03-03",
        "phone": "2134567890",
        "karaoke?": "off",
        "name": "yolo",
        "description": "descript",
        "location": "yo",
        "time": "15:03",
        "email": "a@b.c",
        "duration": "4",
        "csrf": csrf_token,
    }


@fixture
def form_params_no_karaoke(csrf_token):
    return {
        "csrf": csrf_token,
        "date": "0003-03-03",
        "description": "Some words to meet minumum.",
        "duration": "3",
        "email": "a@b.c",
        "location": "YOLOLLLL",
        "name": "Nath",
        "phone": "4123271341",
        "time": "03:03",
    }


@fixture
def session_data_form_submitted(session_data):
    session_data["contact"] = {"form": "submitted"}
    return session_data


@fixture
def session_data_with_csrf(csrf_token, session_data):
    session_data["contact"] = {"csrf": csrf_token}
    return session_data


@fixture
def sns_connection_thread_mock(client_mock, mocker):
    t = mocker.Mock(name="thread")
    t.join.return_value = client_mock
    return t


def test_act_empty_params(connection_thread_mock, session_data):
    assert contact.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_act_clear_params(connection_thread_mock, session_data):
    params = {"form": "clear"}
    assert contact.act(connection_thread_mock, session_data, params) == (session_data, [])


def test_act_not_all_params(connection_thread_mock, session_data):
    params = {"name": "yolo"}
    assert contact.act(connection_thread_mock, session_data, params) == (session_data, [])


def test_act_all_params(
    client_mock,
    connection_thread_mock,
    csrf_token,
    disable_thread_call_maybe,
    env_with_notification_arn,
    form_params,
    session_data_with_csrf,
):
    client_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    observed, _ = contact.act(connection_thread_mock, session_data_with_csrf, form_params)
    assert observed["contact"]["form"] == "submitted"


def test_act_no_karaoke(
    client_mock,
    connection_thread_mock,
    csrf_token,
    disable_thread_call_maybe,
    env_with_notification_arn,
    form_params_no_karaoke,
    session_data_with_csrf,
):
    client_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    observed, _ = contact.act(connection_thread_mock, session_data_with_csrf, form_params_no_karaoke)
    assert observed["contact"]["form"] == "submitted"


def test_act_no_csrf(connection_thread_mock, csrf_token, form_params, session_data):
    observed, _ = contact.act(connection_thread_mock, session_data, form_params)
    assert "form" not in observed["contact"]
    assert "csrf" in observed["contact"]


def test_act_no_duration(
    connection_thread_mock, csrf_token, env_with_notification_arn, form_params, session_data_with_csrf
):
    form_params.pop("duration")
    observed, _ = contact.act(connection_thread_mock, session_data_with_csrf, form_params)
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


def test_contact_connection_holder(
    client_mock,
    connection_thread_mock,
    csrf_token,
    env_with_notification_arn,
    form_params,
    mocker,
    session_data_with_csrf,
    sns_connection_thread_mock,
):
    mocker.patch("lib.contact.sns_client_global_holder", client_mock)
    client_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    observed = contact.act(connection_thread_mock, session_data_with_csrf, form_params)
    expected = (session_data_with_csrf, [])
    assert observed == expected


def test_create_sns_client(mocker):
    boto3_mock = mocker.patch("lib.contact.boto3")
    expected = mocker.Mock(name="mock_sns_client")
    boto3_mock.client.return_value = expected
    observed = contact.create_sns_client()
    assert observed == expected
