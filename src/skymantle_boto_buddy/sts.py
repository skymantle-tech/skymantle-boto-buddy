import logging
import os
from typing import Any

from boto3 import Session
from botocore.client import Config

from skymantle_boto_buddy import EnableCache, get_boto3_client

logger = logging.getLogger()


def get_sts_client(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_client("sts", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_sts_client()


def get_caller_identity(region_name: str | None = None, session: Session = None) -> dict:
    sts_client = get_sts_client(region_name, session)
    return sts_client.get_caller_identity()


def get_caller_account(region_name: str | None = None, session: Session = None) -> str:
    return get_caller_identity(region_name, session)["Account"]
