from invoke import Collection, Task, task
from typing import cast
import boto3
import csv

from .image import images
from .mix import mix
from .section import section
from .toasts import toasts


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


data = Collection()
data.add_collection(section, "section")
data.add_collection(images, "images")
data.add_collection(mix, "mix")
data.add_collection(toasts, "toast")
data.add_task(cast(Task, load_ddb_table))
