from invoke import Collection, Task, task
from typing import cast
import boto3


@task
def remove(_c, table_name: str, mix_id: str) -> bool:
    ddb_client = boto3.client("dynamodb")
    ddb_client.delete_item(TableName=table_name, Key={"pk": {"S": "mixes"}, "sk": {"S": mix_id}})
    return True


@task
def upload(_c, table_name: str, mix_id: str, source: str) -> bool:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    item = {"pk": "mixes", "sk": mix_id, "source": source}
    table.put_item(Item=item)
    return True


mix = Collection("mix")
mix.add_task(cast(Task, upload))
