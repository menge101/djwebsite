from invoke import Collection, Task, task
from typing import cast
from uuid import uuid1
import boto3
import csv


@task
def load_ddb_table(_ctx, table_name, source_file_path):
    rsrc = boto3.resource("dynamodb")
    tbl = rsrc.Table(table_name)
    with open(source_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    for row in rows:
        tbl.put_item(Item=row)
    return True


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
data.add_task(cast(Task, load_ddb_table))
