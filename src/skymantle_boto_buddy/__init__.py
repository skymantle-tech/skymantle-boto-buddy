from enum import Enum
from functools import cache
from typing import Any

import boto3


class EnableCache(Enum):
    YES = 1
    NO = 1


@cache
def get_boto3_session(  # noqa: PLR0913
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    region_name=None,
    botocore_session=None,
    profile_name=None,
) -> boto3.Session:
    return boto3.Session(
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
        region_name,
        botocore_session,
        profile_name,
    )


@cache
def get_boto3_client(  # noqa: PLR0913
    service_name,
    region_name=None,
    api_version=None,
    use_ssl=True,  # noqa: FBT002
    verify=None,
    endpoint_url=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    config=None,
) -> Any:
    return boto3.client(
        service_name,
        region_name,
        api_version,
        use_ssl,
        verify,
        endpoint_url,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
        config,
    )


@cache
def get_boto3_resource(  # noqa: PLR0913
    service_name,
    region_name=None,
    api_version=None,
    use_ssl=True,  # noqa: FBT002
    verify=None,
    endpoint_url=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    config=None,
) -> Any:
    return boto3.resource(
        service_name,
        region_name,
        api_version,
        use_ssl,
        verify,
        endpoint_url,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
        config,
    )
