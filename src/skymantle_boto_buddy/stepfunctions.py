import json
import logging
import os
import time
from typing import Any

from boto3 import Session
from botocore.client import Config

from skymantle_boto_buddy import EnableCache, get_boto3_client

logger = logging.getLogger()


def get_stepfunctions_client(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_client("stepfunctions", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_stepfunctions_client()


def start_execution(
    stepfunction_arn: str, json_input: dict, *, region_name: str | None = None, session: Session = None
) -> dict:
    sf_client = get_stepfunctions_client(region_name, session)
    return sf_client.start_execution(stateMachineArn=stepfunction_arn, input=json.dumps(json_input))


def start_sync_execution(
    stepfunction_arn: str, json_input: dict, *, region_name: str | None = None, session: Session = None
) -> dict:
    sf_client = get_stepfunctions_client(region_name, session)
    return sf_client.start_sync_execution(stateMachineArn=stepfunction_arn, input=json.dumps(json_input))


def describe_execution(execution_arn: str, *, region_name: str | None = None, session: Session = None) -> dict:
    sf_client = get_stepfunctions_client(region_name, session)
    return sf_client.describe_execution(executionArn=execution_arn)


def start_with_wait_for_completion(
    stepfunction_arn: str,
    json_input: dict,
    max_retries: int = 5,
    delay_in_seconds: int = 1,
    *,
    region_name: str | None = None,
    session: Session = None,
) -> dict:
    sf_client = get_stepfunctions_client(region_name, session)
    response = sf_client.start_execution(stateMachineArn=stepfunction_arn, input=json.dumps(json_input))

    execution_arn = response["executionArn"]
    attempts = 1
    while attempts <= max_retries:
        response = sf_client.describe_execution(executionArn=execution_arn)

        if response["status"] in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            return response

        # RUNNING or PENDING_REDRIVE
        attempts += 1
        time.sleep(delay_in_seconds)

    return response
