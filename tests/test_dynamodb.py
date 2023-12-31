import os
from importlib import reload

import boto3
import pytest
from boto3 import Session
from boto3.dynamodb.conditions import Key
from botocore.exceptions import NoRegionError
from moto import mock_dynamodb
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, dynamodb
from skymantle_boto_buddy.dynamodb import ReturnValues


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_dynamodb
def test_no_default_region():
    reload(dynamodb)

    with pytest.raises(NoRegionError) as e:
        dynamodb.get_item("some_table", {"PK": "some_pk"})

    assert str(e.value) == "You must specify a region."


@mock_dynamodb
def test_manual_region():
    reload(dynamodb)

    client = dynamodb.get_dynamodb_resource("ca-central-1")

    assert type(client).__name__ == "dynamodb.ServiceResource"


@mock_dynamodb
def test_manual_session():
    reload(dynamodb)

    client = dynamodb.get_dynamodb_resource("ca-central-1", Session())

    assert type(client).__name__ == "dynamodb.ServiceResource"


@mock_dynamodb
def test_dynamodb_client_cache():
    reload(dynamodb)

    db_client_cached_one = dynamodb.get_dynamodb_resource("ca-central-1", enable_cache=EnableCache.YES)
    db_client_cached_two = dynamodb.get_dynamodb_resource("ca-central-1", enable_cache=EnableCache.YES)

    assert id(db_client_cached_one) == id(db_client_cached_two)

    db_client_no_cache_one = dynamodb.get_dynamodb_resource("ca-central-1", enable_cache=EnableCache.NO)
    db_client_no_cache_two = dynamodb.get_dynamodb_resource("ca-central-1", enable_cache=EnableCache.NO)

    assert id(db_client_no_cache_one) != id(db_client_no_cache_two)
    assert id(db_client_cached_one) != id(db_client_no_cache_one)
    assert id(db_client_cached_one) != id(db_client_no_cache_two)


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_put_item_simplified():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
    )

    response = dynamodb.put_item_simplified("some_table", {"PK": "some_pk", "Name": "some value"})
    assert response["ResponseMetadata"]["RetryAttempts"] == 0

    response = dynamodb_client.get_item(TableName="some_table", Key={"PK": {"S": "some_pk"}})

    assert response["Item"] == {"PK": {"S": "some_pk"}, "Name": {"S": "some value"}}


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_update_item_simplified():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk"}, "Name": {"S": "some value"}})

    response = dynamodb.update_item_simplified(
        "some_table", {"PK": "some_pk"}, {"Name": "some new value"}, ReturnValues.ALL_OLD
    )
    assert response["Attributes"]["Name"] == "some value"

    response = dynamodb_client.get_item(TableName="some_table", Key={"PK": {"S": "some_pk"}})

    assert response["Item"] == {"PK": {"S": "some_pk"}, "Name": {"S": "some new value"}}


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_get_item():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk"}, "Name": {"S": "some value"}})

    item = dynamodb.get_item("some_table", {"PK": "some_pk"})

    assert item["Name"] == "some value"


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_delete_item():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk"}, "Name": {"S": "some value"}})

    dynamodb.delete_item("some_table", {"PK": "some_pk"})

    response = dynamodb_client.get_item(TableName="some_table", Key={"PK": {"S": "some_pk"}})

    assert response.get("Item") is None


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_query_no_paging():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "Name", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "Index1",
                "KeySchema": [{"AttributeName": "Name", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_1"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_2"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_3"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_4"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_5"}, "Name": {"S": "some other value"}})

    result = dynamodb.query_no_paging("some_table", Key("Name").eq("some value"), "Index1")

    assert len(result) == 4
    assert result[0] == {"PK": "some_pk_1", "Name": "some value"}
    assert result[1] == {"PK": "some_pk_2", "Name": "some value"}
    assert result[2] == {"PK": "some_pk_3", "Name": "some value"}
    assert result[3] == {"PK": "some_pk_4", "Name": "some value"}


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_query_no_paging_with_limit():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "Name", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "Index1",
                "KeySchema": [{"AttributeName": "Name", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_1"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_2"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_3"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_4"}, "Name": {"S": "some value"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_5"}, "Name": {"S": "some value"}})

    result = dynamodb.query_no_paging("some_table", Key("Name").eq("some value"), "Index1", 1)

    assert len(result) == 5
    assert result[0] == {"PK": "some_pk_1", "Name": "some value"}
    assert result[1] == {"PK": "some_pk_2", "Name": "some value"}
    assert result[2] == {"PK": "some_pk_3", "Name": "some value"}
    assert result[3] == {"PK": "some_pk_4", "Name": "some value"}
    assert result[4] == {"PK": "some_pk_5", "Name": "some value"}


@mock_dynamodb
@pytest.mark.usefixtures("environment")
def test_query_no_paging_no_index():
    reload(dynamodb)

    dynamodb_client = boto3.client("dynamodb")

    dynamodb_client.create_table(
        BillingMode="PAY_PER_REQUEST",
        TableName="some_table",
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "Name", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "Name", "KeyType": "RANGE"},
        ],
    )
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_1"}, "Name": {"S": "some value 1"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_1"}, "Name": {"S": "some value 2"}})
    dynamodb_client.put_item(TableName="some_table", Item={"PK": {"S": "some_pk_2"}, "Name": {"S": "some value 3"}})

    result = dynamodb.query_no_paging("some_table", Key("PK").eq("some_pk_1"))

    assert len(result) == 2
    assert result[0] == {"PK": "some_pk_1", "Name": "some value 1"}
    assert result[1] == {"PK": "some_pk_1", "Name": "some value 2"}
