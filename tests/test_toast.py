from datetime import datetime

from lib import toast


def test_delete(connection_thread_mock, client_mock, toast_obj):
    client_mock.delete_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    assert toast_obj.delete(connection_thread_mock)


def test_key(toast_obj, toast_id, session_id):
    expected = {"pk": f"{session_id}-toast", "sk": toast_id}
    observed = toast_obj.key()
    assert observed == expected


def test_marshal(toast_db_record, toast_obj, toast_id, toast_message, session_id, toast_ttl):
    expected = toast_db_record
    observed = toast_obj.marshal()
    assert observed == expected


def test_persist(connection_thread_mock, client_mock, toast_obj):
    client_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    assert toast_obj.persist(connection_thread_mock)


def test_render(toast_obj):
    expected = '<div class="alert alert-info" _="on click remove me"><span>yolo</span></div>'
    observed = toast_obj.render().string()
    assert observed == expected


def test_render_warning(session_id, toast_id, toast_message, toast_ttl):
    toast_obj = toast.Toast(session_id, toast_message, toast_id=toast_id, ttl=toast_ttl, level="warning")
    expected = '<div class="alert alert-warning" _="on click remove me"><span>yolo</span></div>'
    observed = toast_obj.render().string()
    assert observed == expected


def test_render_error(session_id, toast_id, toast_message, toast_ttl):
    toast_obj = toast.Toast(session_id, toast_message, toast_id=toast_id, ttl=toast_ttl, level="error")
    expected = '<div class="alert alert-error" _="on click remove me"><span>yolo</span></div>'
    observed = toast_obj.render().string()
    assert observed == expected


def test_render_none(session_id, toast_id, toast_message, toast_ttl):
    toast_obj = toast.Toast(session_id, toast_message, toast_id=toast_id, ttl=toast_ttl)
    expected = '<div class="alert" _="on click remove me"><span>yolo</span></div>'
    observed = toast_obj.render().string()
    assert observed == expected


def test_render_success(session_id, toast_id, toast_message, toast_ttl):
    toast_obj = toast.Toast(session_id, toast_message, toast_id=toast_id, ttl=toast_ttl, level="success")
    expected = '<div class="alert alert-success" _="on click remove me"><span>yolo</span></div>'
    observed = toast_obj.render().string()
    assert observed == expected


def test_unmarshal(toast_db_record, toast_obj):
    assert toast_obj == toast.Toast.unmarshal(toast_db_record)


def test__eq__(toast_obj, session_id, toast_id, toast_message, toast_ttl):
    assert toast_obj != 34
    different_toast = toast.Toast(session_id="0", toast_id="3", message="yala", ttl=9)
    assert toast_obj != different_toast
    different_toast = toast.Toast(session_id=session_id, toast_id="3", message="yala", ttl=9)
    assert toast_obj != different_toast
    different_toast = toast.Toast(session_id=session_id, toast_id=toast_id, message="yala", ttl=9)
    assert toast_obj != different_toast
    different_toast = toast.Toast(session_id=session_id, toast_id=toast_id, message=toast_message, ttl=9)
    assert toast_obj != different_toast
    different_toast = toast.Toast(session_id=session_id, toast_id=toast_id, message=toast_message, ttl=toast_ttl)
    assert toast_obj == different_toast


def test_expiration(mocker):
    datetime_mock = mocker.patch("lib.toast.datetime")
    datetime_mock.now.return_value = datetime(2020, 1, 1, 0, 0)
    observed = toast.Toast.expiration()
    expected = 1577855400
    assert observed == expected


def test_create(connection_thread_mock, session_id, toast_message, mocker, toast_id, client_mock):
    mocker.patch("lib.toast.uuid1", return_value=toast_id)
    client_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    observed = toast.create(connection_thread_mock, session_id, toast_message)
    assert observed == toast_id


def test_destroy(client_mock, connection_thread_mock, toast_obj):
    client_mock.delete_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    assert toast.destroy(connection_thread_mock, [toast_obj])


def test_get(client_mock, connection_thread_mock, session_id, toast_id, toast_db_record, toast_obj):
    client_mock.get_item.return_value = {"Item": toast_db_record}
    expected = toast_obj
    observed = toast.get(connection_thread_mock, session_id, toast_id)
    assert observed == expected


def test_query(client_mock, connection_thread_mock, session_id, toast_db_record, toast_obj):
    client_mock.query.return_value = {"Items": [toast_db_record]}
    expected = [toast_obj]
    observed = toast.query(connection_thread_mock, session_id)
    assert observed == expected
