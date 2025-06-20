from lib import session
from pytest import fixture


@fixture
def session_data(session_id):
    return {
        "local": "en",
        "id_": session_id,
        "pk": "session",
        "sk": session_id,
        "logo": {"state": "rotate"},
    }


def test_update_session(connection_thread_mock, session_data, table):
    result = session.update_session(connection_thread_mock, session_data, "logo")
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
