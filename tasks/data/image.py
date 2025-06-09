from invoke import Collection, Task, task
from typing import cast
import boto3


@task
def remove(_c, table_name: str, bucket_name: str, url: str) -> bool:
    s3_removal_success: bool = _remove_s3(bucket_name, url)
    ddb_removal_success: bool = _remove_ddb(table_name, url)
    if all([s3_removal_success, ddb_removal_success]):
        print(f"Successfully removed image {url} from s3 and ddb")
        return True
    else:
        return False


@task
def upload(_c, table_name: str, bucket_name: str, path_to_file: str, url: str, alt_text: str) -> bool:
    s3_success: bool = _upload_to_s3(bucket_name, url, path_to_file)
    ddb_success: bool = _update_ddb_table(table_name, url, alt_text)
    if all([s3_success, ddb_success]):
        print(f"Uploaded image from {path_to_file} to s3 and updated app links with {url} url")
        return True
    return False


def _remove_ddb(table_name: str, url: str) -> bool:
    ddb_client = boto3.client("dynamodb")
    ddb_client.delete_item(TableName=table_name, Key={"pk": {"S": "images"}, "sk": {"S": url}})
    return True


def _remove_s3(bucket_name: str, url: str) -> bool:
    client = boto3.client("s3")
    client.delete_object(Bucket=bucket_name, Key=f"images/{url}")
    return True


def _update_ddb_table(table_name: str, url: str, alt_text: str) -> bool:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    item = {"pk": "images", "sk": url, "url": f"/images/{url}", "alt_text": alt_text}
    table.put_item(Item=item)
    return True


def _upload_to_s3(bucket_name: str, url: str, path_to_file: str) -> bool:
    client = boto3.client("s3")
    client.upload_file(path_to_file, bucket_name, f"images/{url}")
    return True


images = Collection("images")
images.add_task(cast(Task, remove))
images.add_task(cast(Task, upload))
