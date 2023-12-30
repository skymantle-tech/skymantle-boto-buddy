import logging
import os
from enum import Enum
from typing import Any

import skymantle_boto_buddy
from skymantle_boto_buddy import EnableCache

logger = logging.getLogger()


class ReturnValues(Enum):
    NONE = 1
    ALL_OLD = 2
    UPDATED_OLD = 3
    ALL_NEW = 4
    UPDATED_NEW = 5


def get_dynamodb_resource(region_name: str, enable_cache: EnableCache = EnableCache.YES):
    if enable_cache == EnableCache.YES:
        return skymantle_boto_buddy.get_boto3_resource("dynamodb", region_name)
    else:
        return skymantle_boto_buddy.get_boto3_resource.__wrapped__("dynamodb", region_name)


default_region: str = os.environ.get("AWS_DEFAULT_REGION", None)
if default_region:
    get_dynamodb_resource(default_region)


def get_table(table_name: str, region_name: str = default_region, enable_cache: EnableCache = EnableCache.YES):
    dynamo_db = get_dynamodb_resource(region_name, enable_cache)
    return dynamo_db.Table(table_name)


def put_item_simplified(
    table_name: str,
    item: dict[str, Any],
    return_values: ReturnValues = ReturnValues.NONE,
    region_name: str = default_region,
) -> dict:
    table = get_table(table_name, region_name)

    response = table.put_item(Item=item, ReturnValues=return_values.name)

    return response


def update_item_simplified(
    table_name: str,
    key: dict[str, Any],
    update_map: dict[str, Any],
    return_values: ReturnValues = ReturnValues.NONE,
    region_name: str = default_region,
):
    table = get_table(table_name, region_name)

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


def get_item(table_name: str, key: dict[str, Any], region_name: str = default_region) -> dict:
    table = get_table(table_name, region_name)

    response = table.get_item(Key=key)

    item = response.get("Item", {})
    return item


def delete_item(table_name: str, key: dict[str, Any], region_name: str = default_region) -> None:
    table = get_table(table_name, region_name)

    table.delete_item(Key=key)


def query_no_paging(
    table_name: str, key_condition_expression, index_name: str | None = None, region_name: str = default_region
) -> list[dict[str, Any]]:
    table = get_table(table_name, region_name)

    query_kwargs = {
        "KeyConditionExpression": key_condition_expression,
    }

    if index_name:
        query_kwargs["IndexName"] = index_name

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
