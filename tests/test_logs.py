import os
from importlib import reload

import pytest
from boto3 import Session
from moto import mock_logs
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, logs


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


# @mock_logs
# def test_no_default_region():
#     reload(logs)

#     with pytest.raises(NoRegionError) as e:
#         logs.get_parameter("some_key")

#     assert str(e.value) == "You must specify a region."


@mock_logs
def test_manual_region():
    reload(logs)

    client = logs.get_logs_client("ca-central-1")

    assert type(client).__name__ == "CloudWatchLogs"


@mock_logs
def test_manual_session():
    reload(logs)

    client = logs.get_logs_client("ca-central-1", Session())

    assert type(client).__name__ == "CloudWatchLogs"


@mock_logs
@pytest.mark.usefixtures("environment")
def test_logs_client_cache():
    reload(logs)

    logs_client_cached_one = logs.get_logs_client(enable_cache=EnableCache.YES)
    logs_client_cached_two = logs.get_logs_client(enable_cache=EnableCache.YES)

    assert logs_client_cached_one == logs_client_cached_two

    logs_client_no_cache_one = logs.get_logs_client(enable_cache=EnableCache.NO)
    logs_client_no_cache_two = logs.get_logs_client(enable_cache=EnableCache.NO)

    assert logs_client_no_cache_one != logs_client_no_cache_two
    assert logs_client_cached_one != logs_client_no_cache_one
    assert logs_client_cached_one != logs_client_no_cache_two
