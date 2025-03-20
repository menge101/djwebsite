from invoke import Context
from pytest import fixture


from tasks import data


@fixture
def boto3_mock(mocker):
    return mocker.patch("tasks.data.boto3")


@fixture
def context():
    return Context()


@fixture
def table_name():
    return "development-djweb-webapplicationconstructdata33DBB228-15TRMOJDNRQ12"


@fixture
def url():
    return "https://img.daisyui.com/images/stock/photo-1559703248-dcaaec9fab78.webp"


def test_upload_image(context, table_name, url):
    assert data.upload_image(context, table_name, url, "yolo")
