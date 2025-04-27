from lib import types
from pytest import fixture


@fixture
def ddb_obj():
    return {
        "a": {"S": "aye"},
        "b-map": {"M": {"b": {"S": "bee"}, "be": {"S": "beee"}}},
        "c-list": {"L": [{"S": "a"}, {"S": "b"}, {"S": "c"}]},
    }


@fixture
def py_obj():
    return {"a": "aye", "b-map": {"b": "bee", "be": "beee"}, "c-list": ["a", "b", "c"]}


def test_dict_to_ddb(ddb_obj, py_obj):
    observed = types.dict_to_ddb(py_obj)
    expected = ddb_obj
    assert observed == expected


def test_ddb_to_dict(ddb_obj, py_obj):
    observed = types.ddb_to_dict(ddb_obj)
    expected = py_obj
    assert observed == expected
