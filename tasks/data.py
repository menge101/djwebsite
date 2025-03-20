from invoke import Collection, Task, task
from typing import cast
from uuid import uuid1
import boto3


@task
def upload_image(_c, table_name, url, alt_text):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    item = {"pk": "images", "sk": str(uuid1().int), "url": url, "alt_text": alt_text}
    table.put_item(Item=item)
    print(f"Added image {url} to app")
    return True


data = Collection()
data.add_task(cast(Task, upload_image))
