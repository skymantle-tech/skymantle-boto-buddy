import logging
import os

from botocore.exceptions import ClientError

from skymantle_boto_buddy import EnableCache, get_boto3_client

logger = logging.getLogger()


def get_cloudformation_client(region_name: str, enable_cache: EnableCache = EnableCache.YES):
    if enable_cache == EnableCache.YES:
        return get_boto3_client("cloudformation", region_name)
    else:
        return get_boto3_client.__wrapped__("cloudformation", region_name)


default_region: str = os.environ.get("AWS_DEFAULT_REGION")
if default_region:
    get_cloudformation_client(default_region)


def describe_stacks(stack_name: str, region_name: str = default_region) -> dict:
    try:
        response = get_cloudformation_client(region_name).describe_stacks(StackName=stack_name)
    except ClientError as e:
        raise Exception(f"Cannot find stack {stack_name} in {region_name}") from e

    return response


def get_stack_outputs(stack_name: str, region_name: str = default_region) -> dict:
    response = describe_stacks(stack_name, region_name)

    stack_outputs = response["Stacks"][0]["Outputs"]

    outputs = {}
    for stack_output in stack_outputs:
        outputs[stack_output["OutputKey"]] = stack_output["OutputValue"]

    return outputs
