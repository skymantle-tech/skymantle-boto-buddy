import os
from importlib import reload

import pytest
from boto3 import Session
from moto import mock_aws
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, sts


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_aws
def test_manual_region():
    reload(sts)

    client = sts.get_sts_client("ca-central-1")

    assert type(client).__name__ == "STS"


@mock_aws
def test_manual_session():
    reload(sts)

    client = sts.get_sts_client("ca-central-1", Session())

    assert type(client).__name__ == "STS"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_sts_client_cache():
    reload(sts)

    sts_client_cached_one = sts.get_sts_client(enable_cache=EnableCache.YES)
    sts_client_cached_two = sts.get_sts_client(enable_cache=EnableCache.YES)

    assert sts_client_cached_one == sts_client_cached_two

    sts_client_no_cache_one = sts.get_sts_client(enable_cache=EnableCache.NO)
    sts_client_no_cache_two = sts.get_sts_client(enable_cache=EnableCache.NO)

    assert sts_client_no_cache_one != sts_client_no_cache_two
    assert sts_client_cached_one != sts_client_no_cache_one
    assert sts_client_cached_one != sts_client_no_cache_two


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_account():
    reload(sts)

    response = sts.get_caller_account()
    assert response == "123456789012"
