import pytest

from lib import toast


@pytest.fixture
def message():
    return "yolo"


@pytest.fixture
def toast_obj_persisted(table, connection_thread_mock, toast_obj):
    toast_obj.persist(connection_thread_mock)
    return toast_obj


@pytest.fixture
def toast_obj(session_id, message):
    return toast.Toast(session_id, message)


def test_delete(table, connection_thread_mock, toast_obj_persisted):
    assert toast_obj_persisted.delete(connection_thread_mock)


def test_persist(table, connection_thread_mock, toast_obj):
    assert toast_obj.persist(connection_thread_mock)
