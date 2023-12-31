from enum import Enum
from functools import cache
from typing import Any

import boto3
from boto3 import Session
from botocore.client import Config


class EnableCache(Enum):
    YES = 1
    NO = 2


def get_boto3_client_v2(
    service_name: str,
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    """Create a low-level service client by name. A wrapper for __get_boto3_client_v2,
    because calling the method with default values and passing in default values are
    not treated as equivalent.

    __get_boto3_client_v2("s3") != __get_boto3_client_v2("s3", None, None, None)

    Args:
        service_name (str): The name of a service, e.g. 's3' or 'ec2'.
        region_name (str | None, optional): The name of the region associated with the client. Defaults to None.
        session (Session, optional): A session stores configuration state and allows you to create service
            clients and resources. Defaults to None.
        config (Config, optional): Advanced client configuration options. Defaults to None.
        enable_cache (EnableCache, optional): Get the cached version or not. Defaults to EnableCache.YES.

    Returns:
        Any: Service client instance
    """
    if enable_cache == EnableCache.YES:
        return __get_boto3_client_v2(service_name, region_name, session, config)
    else:
        return __get_boto3_client_v2.__wrapped__(service_name, region_name, session, config)


@cache
def __get_boto3_client_v2(service_name: str, region_name: str, session: Session, config: Config) -> Any:
    """Create a low-level service client by name. Used Ben Kehoe's suggestion for handling session.

    https://ben11kehoe.medium.com/boto3-sessions-and-why-you-should-use-them-9b094eb5ca8e

    Args:
        service_name (str): The name of a service, e.g. 's3' or 'ec2'.
        region_name (str): The name of the region associated with the client.
        session (Session): A session stores configuration state and allows you to create service clients and resources.
        config (Config): Advanced client configuration options.

    Returns:
        Any: Service client instance
    """
    if not session:
        session = boto3._get_default_session()
    return session.client(service_name, region_name=region_name, config=config)


def get_boto3_resource_v2(
    service_name: str,
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    """Create a resource service client by name. A wrapper for __get_boto3_resource_v2,
    because calling the method with default values and passing in default values are
    not treated as equivalent.

    __get_boto3_resource_v2("s3") != __get_boto3_resource_v2("s3", None, None, None)

    Args:
        service_name (str): The name of a service, e.g. 's3' or 'ec2'.
        region_name (str | None, optional): The name of the region associated with the client. Defaults to None.
        session (Session, optional): A session stores configuration state and allows you to create service
            clients and resources. Defaults to None.
        config (Config, optional): Advanced client configuration options. Defaults to None.
        enable_cache (EnableCache, optional): Get the cached version or not. Defaults to EnableCache.YES.

    Returns:
        Any: Subclass of :py:class:`~boto3.resources.base.ServiceResource`
    """
    if enable_cache == EnableCache.YES:
        return __get_boto3_resource_v2(service_name, region_name, session, config)
    else:
        return __get_boto3_resource_v2.__wrapped__(service_name, region_name, session, config)


@cache
def __get_boto3_resource_v2(service_name: str, region_name: str, session: Session, config: Config) -> Any:
    """Create a resource service client by name. Used Ben Kehoe's suggestion for handling session.

    https://ben11kehoe.medium.com/boto3-sessions-and-why-you-should-use-them-9b094eb5ca8e

    Args:
        service_name (str): The name of a service, e.g. 's3' or 'ec2'.
        region_name (str): The name of the region associated with the client.
        session (Session): A session stores configuration state and allows you to create service clients and resources.
        config (Config): Advanced client configuration options.

    Returns:
        Any: Subclass of :py:class:`~boto3.resources.base.ServiceResource`
    """
    if not session:
        session = boto3._get_default_session()
    return session.resource(service_name, region_name=region_name, config=config)
