import os
from importlib import reload

import boto3
import pytest
from moto import mock_ssm
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, ssm


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1"},
    )


@mock_ssm
def test_get_parameter_no_default_region():
    reload(ssm)

    ssm_client = boto3.client("ssm", region_name="ca-central-1")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    result = ssm.get_parameter("some_key", region_name="ca-central-1")

    assert result == "some value"


@mock_ssm
def test_ssm_client_cache():
    reload(ssm)

    ssm_client = boto3.client("ssm", region_name="ca-central-1")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    ssm_client_cached_one = ssm.get_ssm_client("ca-central-1", EnableCache.YES)
    ssm_client_cached_two = ssm.get_ssm_client("ca-central-1", EnableCache.YES)

    assert ssm_client_cached_one == ssm_client_cached_two

    ssm_client_no_cache_one = ssm.get_ssm_client("ca-central-1", EnableCache.NO)
    ssm_client_no_cache_two = ssm.get_ssm_client("ca-central-1", EnableCache.NO)

    assert ssm_client_no_cache_one != ssm_client_no_cache_two
    assert ssm_client_cached_one != ssm_client_no_cache_one
    assert ssm_client_cached_one != ssm_client_no_cache_two


@mock_ssm
@pytest.mark.usefixtures("environment")
def test_get_parameter():
    reload(ssm)

    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    result = ssm.get_parameter("some_key")

    assert result == "some value"


@mock_ssm
@pytest.mark.usefixtures("environment")
def test_get_parameter_decrypted():
    reload(ssm)

    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(Name="some_key", Type="String", Value="some value")

    result = ssm.get_parameter_decrypted("some_key")

    assert result == "some value"
