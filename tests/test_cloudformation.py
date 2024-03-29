import json
import os
from importlib import reload

import boto3
import pytest
from boto3 import Session
from moto import mock_aws
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, cloudformation

cfn_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "sample template",
    "Resources": {
        "S3Bucket": {
            "Type": "AWS::S3::Bucket",
            "DeletionPolicy": "Retain",
        },
    },
    "Outputs": {
        "S3Bucket": {
            "Value": {"Ref": "S3Bucket"},
            "Description": "An S3 Bucket",
        },
    },
}


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ca-central-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_aws
def test_manual_region():
    reload(cloudformation)

    client = cloudformation.get_cloudformation_client("ca-central-1")

    assert type(client).__name__ == "CloudFormation"


@mock_aws
def test_manual_session():
    reload(cloudformation)

    client = cloudformation.get_cloudformation_client("ca-central-1", Session())

    assert type(client).__name__ == "CloudFormation"


@mock_aws
def test_cloudformation_client_cache():
    reload(cloudformation)

    cfn_client_cached_one = cloudformation.get_cloudformation_client("ca-central-1", enable_cache=EnableCache.YES)
    cfn_client_cached_two = cloudformation.get_cloudformation_client("ca-central-1", enable_cache=EnableCache.YES)

    assert cfn_client_cached_one == cfn_client_cached_two

    cfn_client_no_cache_one = cloudformation.get_cloudformation_client("ca-central-1", enable_cache=EnableCache.NO)
    cfn_client_no_cache_two = cloudformation.get_cloudformation_client("ca-central-1", enable_cache=EnableCache.NO)

    assert cfn_client_no_cache_one != cfn_client_no_cache_two
    assert cfn_client_cached_one != cfn_client_no_cache_one
    assert cfn_client_cached_one != cfn_client_no_cache_two


@mock_aws
@pytest.mark.usefixtures("environment")
def test_describe_stacks():
    reload(cloudformation)

    cfn_client = boto3.client("cloudformation", region_name="ca-central-1")
    cfn_client.create_stack(StackName="some_stack", TemplateBody=json.dumps(cfn_template))

    response = cloudformation.describe_stacks("some_stack")

    assert response["Stacks"][0]["StackName"] == "some_stack"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_describe_stacks_no_stack():
    reload(cloudformation)

    with pytest.raises(Exception) as e:
        cloudformation.describe_stacks("some_stack")

    assert str(e.value) == "Cannot find stack some_stack in ca-central-1"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_stack_outputs():
    reload(cloudformation)

    cfn_client = boto3.client("cloudformation", region_name="ca-central-1")
    cfn_client.create_stack(StackName="some_stack", TemplateBody=json.dumps(cfn_template))

    outputs = cloudformation.get_stack_outputs("some_stack")

    assert "some_stack-s3bucket-" in outputs["S3Bucket"]
