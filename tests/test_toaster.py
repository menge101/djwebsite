from lib import toaster


def test_act():
    session_data = {"yo:lo"}
    observed = toaster.act("datatable", session_data, {})
    expected = session_data, []
    assert observed == expected


def test_build(client_mock, connection_thread_mock, session_data, toast_db_record):
    client_mock.query.return_value = {"Items": [toast_db_record]}
    client_mock.delete_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    response = toaster.build(connection_thread_mock, session_data)
    expected = 200
    observed = response["statusCode"]
    assert observed == expected
