from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from decimal import Decimal
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import AttributeValueTypeDef
from typing import Any, Mapping, NewType, Sequence, Set, Union

ConnectionThreadResultType = NewType("ConnectionThreadResultType", tuple[str, DynamoDBClient, Table])

DynamoDBUpdateItemKey = NewType(
    "DynamoDBUpdateItemKey",
    Mapping[
        str,
        Union[
            AttributeValueTypeDef,
            Union[
                bytes,
                bytearray,
                str,
                int,
                Decimal,
                bool,
                Set[int],
                Set[Decimal],
                Set[str],
                Set[bytes],
                Set[bytearray],
                Sequence[Any],
                Mapping[str, Any],
                None,
            ],
        ],
    ],
)


def ddb_to_dict(ddb_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in ddb_obj.items()}


def dict_to_ddb(py_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in py_obj.items()}
