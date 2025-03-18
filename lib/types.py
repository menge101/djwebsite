from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table
from typing import NewType


ConnectionThreadResultType = NewType("ConnectionThreadResultType", tuple[str, DynamoDBClient, Table])
