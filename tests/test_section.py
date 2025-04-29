from lib import sections
from pytest import fixture


@fixture
def section(client_mock, table_name):
    return sections.Section("test", "en", "w-1/1", False, client_mock, table_name)


def test_section_render_input(section):
    assert section.render_input().string()
    assert section.render_content().string()


def test_act(connection_thread_mock, session_data):
    assert sections.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_build(client_mock, connection_thread_mock, session_data):
    client_mock.query.return_value = {"Items": [{"pk": {"S": "section"}, "sk": {"S": "none"}, "name": {"S": "test"}}]}
    observed = sections.build(connection_thread_mock, session_data)
    assert observed["statusCode"] == 200


def test_build_active(client_mock, connection_thread_mock, session_data):
    client_mock.query.return_value = {
        "Items": [{"pk": {"S": "section"}, "sk": {"S": "none"}, "active": {"BOOL": "true"}}]
    }
    observed = sections.build(connection_thread_mock, session_data)
    assert observed["statusCode"] == 200
