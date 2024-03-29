import os
from importlib import reload

import pytest
from moto import mock_aws
from pytest_mock import MockerFixture

import skymantle_boto_buddy


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "us-east-1", "BOTO_BUDDY_DISABLE_CACHE": "true"},
    )


@mock_aws
@pytest.mark.usefixtures("environment")
def test_disable_client_cache():
    reload(skymantle_boto_buddy)

    s3_client_cached_one = skymantle_boto_buddy.get_boto3_client("s3")
    s3_client_cached_two = skymantle_boto_buddy.get_boto3_client("s3")

    assert id(s3_client_cached_one) != id(s3_client_cached_two)


@mock_aws
@pytest.mark.usefixtures("environment")
def test_disable_resource_cache():
    reload(skymantle_boto_buddy)

    s3_client_cached_one = skymantle_boto_buddy.get_boto3_resource("s3")
    s3_client_cached_two = skymantle_boto_buddy.get_boto3_resource("s3")

    assert id(s3_client_cached_one) != id(s3_client_cached_two)
