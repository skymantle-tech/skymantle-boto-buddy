import os

import skymantle_boto_buddy
from skymantle_boto_buddy import EnableCache


def get_ssm_client(region_name: str, enable_cache: EnableCache = EnableCache.YES):
    if enable_cache == EnableCache.YES:
        return skymantle_boto_buddy.get_boto3_client("ssm", region_name)
    else:
        return skymantle_boto_buddy.get_boto3_client.__wrapped__("ssm", region_name)


default_region: str = os.environ.get("AWS_DEFAULT_REGION", "")
if default_region:
    get_ssm_client(default_region)


def get_parameter(key: str, region_name: str = default_region) -> str:
    client = get_ssm_client(region_name)
    response = client.get_parameter(Name=key)
    value = response.get("Parameter", {}).get("Value")

    return value


def get_parameter_decrypted(key: str, region_name: str = default_region) -> str:
    client = get_ssm_client(region_name)
    response = client.get_parameter(Name=key, WithDecryption=True)
    value = response.get("Parameter", {}).get("Value")

    return value
