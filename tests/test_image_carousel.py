from lib import image_carousel
from pytest import fixture


@fixture
def image():
    return image_carousel.Image("url", "alt")


@fixture
def mock_id_fn(mocker):
    mocker.patch("lib.image_carousel.id", return_value=1)


def test_image_render(image, mock_id_fn):
    assert image.render().string()


def test_image_render_indicator(image, mock_id_fn):
    assert image.render_indicator().string()


def test_act(connection_thread_mock, session_data):
    assert image_carousel.act(connection_thread_mock, session_data, {}) == (session_data, [])


def test_build(client_mock, connection_thread_mock, session_data):
    client_mock.query.return_value = {"Items": [{"url": {"S": "url1"}, "alt_text": {"S": "alt"}}]}
    observed = image_carousel.build(connection_thread_mock)
    assert observed["statusCode"] == 200
