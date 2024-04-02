import json
import os
from importlib import reload
from unittest.mock import ANY, MagicMock, call

import boto3
import pytest
from boto3 import Session
from moto import mock_aws
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, stepfunctions

simple_definition = (
    '{"Comment": "An example of the Amazon States Language using a choice state.",'
    '"StartAt": "DefaultState",'
    '"States": '
    '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}'
)


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_aws
def test_manual_region():
    reload(stepfunctions)

    client = stepfunctions.get_stepfunctions_client("ca-central-1")

    assert type(client).__name__ == "SFN"


@mock_aws
def test_manual_session():
    reload(stepfunctions)

    client = stepfunctions.get_stepfunctions_client("ca-central-1", Session())

    assert type(client).__name__ == "SFN"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_stepfunctions_client_cache():
    reload(stepfunctions)

    stepfunctions_client_cached_one = stepfunctions.get_stepfunctions_client(enable_cache=EnableCache.YES)
    stepfunctions_client_cached_two = stepfunctions.get_stepfunctions_client(enable_cache=EnableCache.YES)

    assert stepfunctions_client_cached_one == stepfunctions_client_cached_two

    stepfunctions_client_no_cache_one = stepfunctions.get_stepfunctions_client(enable_cache=EnableCache.NO)
    stepfunctions_client_no_cache_two = stepfunctions.get_stepfunctions_client(enable_cache=EnableCache.NO)

    assert stepfunctions_client_no_cache_one != stepfunctions_client_no_cache_two
    assert stepfunctions_client_cached_one != stepfunctions_client_no_cache_one
    assert stepfunctions_client_cached_one != stepfunctions_client_no_cache_two


@mock_aws
@pytest.mark.usefixtures("environment")
def test_start_execution():
    reload(stepfunctions)

    client = boto3.client("stepfunctions")

    sm = client.create_state_machine(
        name="name", definition=str(simple_definition), roleArn="arn:aws:iam::123456789012:role/a_role"
    )

    execution = stepfunctions.start_execution(sm["stateMachineArn"], {"some": "data"})

    assert "arn:aws:states:ca-central-1:123456789012:execution:name" in execution["executionArn"]


@mock_aws
@pytest.mark.usefixtures("environment")
def test_describe_execution():
    reload(stepfunctions)

    client = boto3.client("stepfunctions")

    sm = client.create_state_machine(
        name="name", definition=str(simple_definition), roleArn="arn:aws:iam::123456789012:role/a_role"
    )

    execution = client.start_execution(stateMachineArn=sm["stateMachineArn"], input=json.dumps({"some": "data"}))

    response = stepfunctions.describe_execution(execution["executionArn"])

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert response["executionArn"] == execution["executionArn"]
    # ! Need to look into why the input requires two json.loads
    assert json.loads(json.loads(response["input"])) == {"some": "data"}
    assert response["status"] == "RUNNING"


@pytest.fixture()
def mock_time(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("skymantle_boto_buddy.stepfunctions.time")
    return mock


@mock_aws
@pytest.mark.usefixtures("environment")
def test_start_with_wait_for_completion(mock_time):
    # reload(stepfunctions)

    client = boto3.client("stepfunctions")

    sm = client.create_state_machine(
        name="name", definition=str(simple_definition), roleArn="arn:aws:iam::123456789012:role/a_role"
    )

    response = stepfunctions.start_with_wait_for_completion(sm["stateMachineArn"], {"some": "data"})

    mock_time.sleep.assert_has_calls([call(1), call(1), call(1), call(1), call(1)])
    assert mock_time.sleep.call_count == 5

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    # ! Need to look into why the input requires two json.loads
    assert json.loads(json.loads(response["input"])) == {"some": "data"}
    assert response["status"] == "RUNNING"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_start_with_wait_for_completion_failure(mock_time):
    os.environ["SF_EXECUTION_HISTORY_TYPE"] = "FAILURE"

    client = boto3.client("stepfunctions")

    sm = client.create_state_machine(
        name="name", definition=str(simple_definition), roleArn="arn:aws:iam::123456789012:role/a_role"
    )

    response = stepfunctions.start_with_wait_for_completion(sm["stateMachineArn"], {"some": "data"})

    assert mock_time.sleep.call_count == 0

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    # ! Need to look into why the input requires two json.loads
    assert json.loads(json.loads(response["input"])) == {"some": "data"}
    assert response["status"] == "FAILED"


@pytest.fixture()
def mock_get_boto3_client(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("skymantle_boto_buddy.stepfunctions.get_boto3_client", autospec=True)
    return mock


@pytest.mark.usefixtures("environment")
def test_start_sync_execution(mock_get_boto3_client):
    # ! No Moto support for start_sync_execution
    stepfunctions.start_sync_execution("an_arn", {"some": "data"})

    mock_get_boto3_client.assert_called_once_with("stepfunctions", None, None, None, ANY)
    mock_get_boto3_client.return_value.start_sync_execution.assert_called_once_with(
        stateMachineArn="an_arn", input=json.dumps({"some": "data"})
    )
