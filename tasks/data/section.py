from invoke import Collection, Task, task
from typing import cast, Mapping
import boto3


@task
def create(_c, table_name: str, section_name: str, active: bool = False) -> bool:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    item: Mapping = {"pk": "section", "sk": section_name, "active": active}
    table.put_item(Item=item)
    return True


@task
def remove(_c, table_name: str, section_name: str) -> bool:
    client = boto3.client("dynamodb")
    client.delete_item(TableName=table_name, Key={"sk": section_name, "pk": "section"})
    return True


section = Collection("section")
section.add_task(cast(Task, create))
section.add_task(cast(Task, remove))
