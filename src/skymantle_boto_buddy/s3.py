import csv
import json
import logging
import os
from io import BytesIO
from typing import Any

from botocore.client import Config

import skymantle_boto_buddy
from skymantle_boto_buddy import EnableCache

logger = logging.getLogger()


def get_s3_client(region_name: str, config=None, enable_cache: EnableCache = EnableCache.YES):
    if enable_cache == EnableCache.YES:
        return skymantle_boto_buddy.get_boto3_client("s3", region_name=region_name, config=config)
    else:
        return skymantle_boto_buddy.get_boto3_client.__wrapped__("s3", region_name=region_name, config=config)


default_region: str = os.environ.get("AWS_DEFAULT_REGION")
if default_region:
    get_s3_client(default_region)

input_serializations = {
    "csv": {
        "CSV": {
            "FileHeaderInfo": "Use",
            "AllowQuotedRecordDelimiter": True,
            "RecordDelimiter": "\n",
            "FieldDelimiter": ",",
            "QuoteCharacter": '"',
        },
        "CompressionType": "NONE",
    }
}


def get_object_signed_url(bucket: str, key: str, expires_in: int = 300, region_name: str = default_region):
    s3_client = get_s3_client(region_name, Config(signature_version="s3v4"))

    response = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, HttpMethod="GET", ExpiresIn=expires_in
    )

    return response


def put_object_signed_url(bucket: str, key: str, expires_in: int = 300, region_name: str = default_region):
    s3_client = get_s3_client(region_name, Config(signature_version="s3v4"))

    response = s3_client.generate_presigned_url(
        "put_object", Params={"Bucket": bucket, "Key": key}, HttpMethod="PUT", ExpiresIn=expires_in
    )

    return response


def get_object(bucket: str, key: str, region_name: str = default_region):
    s3_client = get_s3_client(region_name)
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
    )
    return response


def get_object_bytes(bucket: str, key: str, region_name: str = default_region):
    response = get_object(bucket, key, region_name=region_name)
    return response["Body"].read()


def get_object_json(bucket: str, key: str, region_name: str = default_region):
    s3_object = get_object_bytes(bucket, key, region_name=region_name)
    return json.loads(s3_object.decode("utf-8"))


def get_object_csv_reader(bucket: str, key: str, region_name: str = default_region):
    s3_object: bytes = get_object_bytes(bucket, key, region_name=region_name)
    return csv.DictReader(s3_object.decode("utf-8").splitlines(keepends=True))


def upload_fileobj(bucket: str, key: str, object_data: BytesIO, region_name: str = default_region):
    object_data.seek(0)

    s3_client = get_s3_client(region_name)
    response = s3_client.upload_fileobj(Bucket=bucket, Key=key, Fileobj=object_data)

    return response


def put_object(bucket: str, key: str, object_data, region_name: str = default_region):
    s3_client = get_s3_client(region_name)
    response = s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=object_data,
    )

    return response


def put_object_json(bucket: str, key: str, json_object, *, region_name: str = default_region):
    return put_object(bucket, key, json.dumps(json_object), region_name=region_name)


def delete_object(bucket: str, key: str, region_name: str = default_region):
    s3_client = get_s3_client(region_name)

    response = s3_client.delete_object(Bucket=bucket, Key=key)

    return response


def delete_objects(bucket: str, keys: list[str], *, region_name: str = default_region):
    s3_client = get_s3_client(region_name)

    delete_objects = {"Objects": [{"Key": key} for key in keys]}
    response = s3_client.delete_objects(Bucket=bucket, Delete=delete_objects)

    return response


def copy(
    source_bucket: str,
    source_key: str,
    destination_bucket: str,
    destination_key: str,
    region_name: str = default_region,
):
    s3_client = get_s3_client(region_name)

    source = {
        "Bucket": source_bucket,
        "Key": source_key,
    }
    response = s3_client.copy(source, destination_bucket, destination_key)

    return response


def list_objects_v2(
    bucket: str,
    prefix: str,
    max_keys: int | None = None,
    continuation_token: str | None = None,
    region_name: str = default_region,
):
    s3_client = get_s3_client(region_name)

    kwargs = {"Bucket": bucket, "Prefix": prefix}

    if continuation_token:
        kwargs["ContinuationToken"] = continuation_token

    if max_keys:
        kwargs["MaxKeys"] = max_keys

    response = s3_client.list_objects_v2(**kwargs)

    result = {"keys": [item["Key"] for item in response.get("Contents", [])]}

    if response.get("NextContinuationToken"):
        result["next_continuation_token"] = response.get("NextContinuationToken")

    return result


def execute_sql_query_simplified(
    bucket: str,
    key: str,
    query: str,
    input_type: str,
    region_name: str = default_region,
) -> list[Any]:
    """Performs an S3 Select statement against a file in S3.
    The aws region used is the 'DefaultRegion' in os.environ.

    Args:
        bucket (str): The s3 bucket with the file
        key (str): The s3 key to the file
        query (str): The query
        input_type (str): The files format. Currently only the value 'csv' is supported.

    Returns:
        dict: The selected data
    """
    logger.debug(f"Start exection on {bucket}/{key}")
    logger.debug(query)
    input_serialization = input_serializations.get(input_type)

    if not input_serialization:
        msg = f"Input type is not supported: {input_type}"
        raise Exception(msg)

    s3_client = get_s3_client(region_name)
    resp = s3_client.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType="SQL",
        Expression=query,
        InputSerialization=input_serialization,
        OutputSerialization={
            "JSON": {
                "RecordDelimiter": "\n",
            }
        },
    )

    record_list = []
    for event in resp["Payload"]:
        if "Records" in event:
            record_list.append(event["Records"]["Payload"])
    records = "".join(r.decode("utf-8") for r in record_list)

    result_list = [json.loads(item) for item in records.split("\n") if item]
    logger.debug(f"{len(result_list)} record(s) have been selected")
    logger.debug(result_list)

    return result_list
