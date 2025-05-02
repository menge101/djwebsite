from invoke import Context
from pytest import fixture

from tasks import data


@fixture
def boto3_mock(mocker):
    return mocker.patch("tasks.data.boto3")


@fixture
def bucket_name():
    return "test-bucket"


@fixture
def context():
    return Context()


@fixture
def path_to_file():
    return "/path/to/file.png"


@fixture
def table_name():
    return "development-djweb-webapplicationconstructdata33DBB228-15TRMOJDNRQ12"


@fixture
def url():
    return "https://img.daisyui.com/images/stock/photo-1559703248-dcaaec9fab78.webp"


def test_upload_image(boto3_mock, bucket_name, context, path_to_file, table_name, url):
    assert data.upload_image(context, table_name, bucket_name, path_to_file, url, "yolo")
