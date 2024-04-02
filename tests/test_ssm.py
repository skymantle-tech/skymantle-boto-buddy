import os
from importlib import reload

import boto3
import pytest
from boto3 import Session
from moto import mock_aws
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, ssm


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_aws
def test_manual_region():
    reload(ssm)

    client = ssm.get_ssm_client("ca-central-1")

    assert type(client).__name__ == "SSM"


@mock_aws
def test_manual_session():
    reload(ssm)

    client = ssm.get_ssm_client("ca-central-1", Session())

    assert type(client).__name__ == "SSM"


@mock_aws
def test_ssm_client_cache():
    reload(ssm)

    ssm_client_cached_one = ssm.get_ssm_client("ca-central-1", enable_cache=EnableCache.YES)
    ssm_client_cached_two = ssm.get_ssm_client("ca-central-1", enable_cache=EnableCache.YES)

    assert ssm_client_cached_one == ssm_client_cached_two

    ssm_client_no_cache_one = ssm.get_ssm_client("ca-central-1", enable_cache=EnableCache.NO)
    ssm_client_no_cache_two = ssm.get_ssm_client("ca-central-1", enable_cache=EnableCache.NO)

    assert ssm_client_no_cache_one != ssm_client_no_cache_two
    assert ssm_client_cached_one != ssm_client_no_cache_one
    assert ssm_client_cached_one != ssm_client_no_cache_two


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_parameter():
    reload(ssm)

    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    result = ssm.get_parameter("some_key")

    assert result == "some value"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_parameter_decrypted():
    reload(ssm)

    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    result = ssm.get_parameter_decrypted("some_key")

    assert result == "some value"
