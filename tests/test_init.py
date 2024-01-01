import os
from importlib import reload
from io import BytesIO

import boto3
import pytest
from boto3 import Session
from moto import mock_s3
from pytest_mock import MockerFixture

import skymantle_boto_buddy


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "us-east-1", "BOTO_BUDDY_DISABLE_CACHE": "true"},
    )


@mock_s3
@pytest.mark.usefixtures("environment")
def test__client_cache():
    reload(skymantle_boto_buddy)

    sts_client_cached_one = skymantle_boto_buddy.get_boto3_client("sts")
    sts_client_cached_two = skymantle_boto_buddy.get_boto3_client("sts")

    assert sts_client_cached_one != sts_client_cached_two


@mock_s3
@pytest.mark.usefixtures("environment")
def test__client_cache():
    reload(skymantle_boto_buddy)

    s3_client_cached_one = skymantle_boto_buddy.get_boto3_resource("s3")
    s3_client_cached_two = skymantle_boto_buddy.get_boto3_resource("s3")

    assert id(s3_client_cached_one) != id(s3_client_cached_two)
