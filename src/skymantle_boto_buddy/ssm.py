import os
from typing import Any

from boto3 import Session
from botocore.client import Config

from skymantle_boto_buddy import EnableCache, get_boto3_client


def get_ssm_client(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_client("ssm", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_ssm_client()


def get_parameter(key: str, *, region_name: str | None = None, session: Session = None) -> str:
    client = get_ssm_client(region_name, session)

    response = client.get_parameter(Name=key)
    value = response.get("Parameter", {}).get("Value")

    return value


def get_parameter_decrypted(key: str, *, region_name: str | None = None, session: Session = None) -> str:
    client = get_ssm_client(region_name, session)

    response = client.get_parameter(Name=key, WithDecryption=True)
    value = response.get("Parameter", {}).get("Value")

    return value
