import logging
import os
from typing import Any

from boto3 import Session
from botocore.client import Config
from botocore.exceptions import ClientError

from skymantle_boto_buddy import EnableCache, get_boto3_client

logger = logging.getLogger()


def get_cloudformation_client(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_client("cloudformation", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_cloudformation_client()


def describe_stacks(stack_name: str, *, region_name: str | None = None, session: Session = None) -> dict:
    cloudformation_client = get_cloudformation_client(region_name, session)
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
    except ClientError as e:
        raise Exception(f"Cannot find stack {stack_name} in {cloudformation_client.meta.region_name}") from e

    return response


def get_stack_outputs(stack_name: str, *, region_name: str | None = None, session: Session = None) -> dict:
    response = describe_stacks(stack_name, region_name=region_name, session=session)

    stack_outputs = response["Stacks"][0]["Outputs"]

    outputs = {}
    for stack_output in stack_outputs:
        outputs[stack_output["OutputKey"]] = stack_output["OutputValue"]

    return outputs
