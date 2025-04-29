from lib import security
from pytest import fixture


@fixture
def html_data():
    return {"html": "<script>alert('hello');</script>"}


@fixture
def sql_data():
    return {"sql": 'INSERT INTO ("pk") VALUES (1);'}


def test_generate_csrf_token():
    assert security.generate_csrf_token()


def test_clean_data_html(html_data):
    observed = security.clean_data(html_data)
    expected = {"html": "%3Cscript%3Ealert%28%27hello%27%29%3B%3C/script%3E"}
    assert observed == expected


def test_clean_data_sql(sql_data):
    observed = security.clean_data(sql_data)
    expected = {"sql": "INSERT%20INTO%20%28%22pk%22%29%20VALUES%20%281%29%3B"}
    assert observed == expected
