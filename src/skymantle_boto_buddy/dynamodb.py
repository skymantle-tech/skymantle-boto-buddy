import logging
import os
from enum import Enum
from typing import Any

from boto3 import Session
from botocore.client import Config

from skymantle_boto_buddy import EnableCache, get_boto3_resource

logger = logging.getLogger()


class ReturnValues(Enum):
    NONE = 1
    ALL_OLD = 2
    UPDATED_OLD = 3
    ALL_NEW = 4
    UPDATED_NEW = 5


def get_dynamodb_resource(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_resource("dynamodb", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_dynamodb_resource()


def get_table(table_name: str, region_name: str | None = None, session: Session = None):
    dynamo_db = get_dynamodb_resource(region_name, session)
    return dynamo_db.Table(table_name)


def put_item_simplified(
    table_name: str,
    item: dict[str, Any],
    return_values: ReturnValues = ReturnValues.NONE,
    region_name: str | None = None,
    session: Session = None,
) -> dict:
    table = get_table(table_name, region_name, session)

    response = table.put_item(Item=item, ReturnValues=return_values.name)

    return response


def update_item_simplified(
    table_name: str,
    key: dict[str, Any],
    update_map: dict[str, Any],
    return_values: ReturnValues = ReturnValues.NONE,
    region_name: str | None = None,
    session: Session = None,
):
    table = get_table(table_name, region_name, session)

    expressions: list[str] = []
    values = {}
    names = {}

    count = 0
    for field, value in update_map.items():
        count += 1
        attribute = f"attr{count}"

        names[f"#{attribute}"] = field
        values[f":{attribute}"] = value
        expressions.append(f"#{attribute} = :{attribute}")

    response = table.update_item(
        Key=key,
        UpdateExpression=f"set {', '.join(expressions)}",
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names,
        ReturnValues=return_values.name,
    )

    return response


def get_item(table_name: str, key: dict[str, Any], region_name: str | None = None, session: Session = None) -> dict:
    table = get_table(table_name, region_name, session)

    response = table.get_item(Key=key)

    item = response.get("Item", {})
    return item


def delete_item(table_name: str, key: dict[str, Any], region_name: str | None = None, session: Session = None) -> None:
    table = get_table(table_name, region_name)

    table.delete_item(Key=key)


def query_no_paging(
    table_name: str,
    key_condition_expression,
    index_name: str | None = None,
    limit: int | None = None,
    region_name: str | None = None,
    session: Session = None,
) -> list[dict[str, Any]]:
    table = get_table(table_name, region_name, session)

    query_kwargs = {
        "KeyConditionExpression": key_condition_expression,
    }

    if index_name:
        query_kwargs["IndexName"] = index_name

    if limit:
        query_kwargs["Limit"] = limit

    items = []

    results = table.query(**query_kwargs)
    for item in results.get("Items", []):
        items.append(item)

    last_evaluated_key = results.get("LastEvaluatedKey", None)
    while last_evaluated_key:
        query_kwargs["ExclusiveStartKey"] = last_evaluated_key

        results = table.query(**query_kwargs)
        for item in results.get("Items", []):
            items.append(item)

        last_evaluated_key = results.get("LastEvaluatedKey", None)

    return items
