import csv
import json
import os
from io import BytesIO
from typing import Any

from boto3 import Session
from botocore.client import Config

from skymantle_boto_buddy import EnableCache, get_boto3_client, get_boto3_resource


def get_s3_client(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_client("s3", region_name, session, config, enable_cache)


def get_s3_resource(
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    return get_boto3_resource("s3", region_name, session, config, enable_cache)


# When imported in a lambda function will load the boto client during initialization
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    get_s3_client()
    get_s3_resource()


def get_bucket(
    name: str,
    *,
    region_name: str | None = None,
    session: Session = None,
    config: Config = None,
    enable_cache: EnableCache = EnableCache.YES,
) -> Any:
    s3 = get_s3_resource(region_name, session, config, enable_cache)
    return s3.Bucket(name)


def get_object_signed_url(
    bucket: str, key: str, expires_in: int = 300, *, region_name: str | None = None, session: Session = None
):
    s3_client = get_s3_client(region_name, session, Config(signature_version="s3v4"))

    response = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, HttpMethod="GET", ExpiresIn=expires_in
    )

    return response


def put_object_signed_url(
    bucket: str, key: str, expires_in: int = 300, *, region_name: str | None = None, session: Session = None
):
    s3_client = get_s3_client(region_name, session, Config(signature_version="s3v4"))

    response = s3_client.generate_presigned_url(
        "put_object", Params={"Bucket": bucket, "Key": key}, HttpMethod="PUT", ExpiresIn=expires_in
    )

    return response


def get_object(bucket: str, key: str, *, region_name: str | None = None, session: Session = None):
    s3_client = get_s3_client(region_name, session)
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
    )
    return response


def get_object_bytes(bucket: str, key: str, *, region_name: str | None = None, session: Session = None):
    response = get_object(bucket, key, region_name=region_name, session=session)
    return response["Body"].read()


def get_object_json(bucket: str, key: str, *, region_name: str | None = None, session: Session = None):
    s3_object = get_object_bytes(bucket, key, region_name=region_name, session=session)
    return json.loads(s3_object.decode("utf-8"))


def get_object_csv_reader(bucket: str, key: str, *, region_name: str | None = None, session: Session = None):
    s3_object: bytes = get_object_bytes(bucket, key, region_name=region_name, session=session)
    return csv.DictReader(s3_object.decode("utf-8").splitlines(keepends=True))


def upload_fileobj(
    bucket: str, key: str, object_data: BytesIO, *, region_name: str | None = None, session: Session = None
):
    object_data.seek(0)

    s3_client = get_s3_client(region_name, session)
    response = s3_client.upload_fileobj(Bucket=bucket, Key=key, Fileobj=object_data)

    return response


def put_object(bucket: str, key: str, object_data, *, region_name: str | None = None, session: Session = None):
    s3_client = get_s3_client(region_name, session)
    response = s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=object_data,
    )

    return response


def put_object_json(bucket: str, key: str, json_object, *, region_name: str | None = None, session: Session = None):
    return put_object(bucket, key, json.dumps(json_object), region_name=region_name, session=session)


def delete_object(bucket: str, key: str, region_name: str | None = None, session: Session = None):
    s3_client = get_s3_client(region_name, session)

    response = s3_client.delete_object(Bucket=bucket, Key=key)

    return response


def delete_objects_simplified(bucket: str, keys: list[str], *, region_name: str | None = None, session: Session = None):
    s3_client = get_s3_client(region_name, session)

    delete_objects = {"Objects": [{"Key": key} for key in keys]}
    response = s3_client.delete_objects(Bucket=bucket, Delete=delete_objects)

    return response


def copy(
    source_bucket: str,
    source_key: str,
    destination_bucket: str,
    destination_key: str,
    *,
    region_name: str | None = None,
    session: Session = None,
):
    s3_client = get_s3_client(region_name, session)

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
    *,
    region_name: str | None = None,
    session: Session = None,
):
    s3_client = get_s3_client(region_name, session)

    kwargs = {"Bucket": bucket, "Prefix": prefix}

    if continuation_token:
        kwargs["ContinuationToken"] = continuation_token

    if max_keys:
        kwargs["MaxKeys"] = max_keys

    response = s3_client.list_objects_v2(**kwargs)

    result = {"keys": [item["Key"] for item in response.get("Contents", [])]}

    if response.get("NextContinuationToken"):
        result["NextContinuationToken"] = response.get("NextContinuationToken")

    return result


def execute_sql_query_simplified(
    bucket: str,
    key: str,
    query: str,
    input_type: str,
    *,
    region_name: str | None = None,
    session: Session = None,
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

    input_serialization = input_serializations.get(input_type)

    if not input_serialization:
        msg = f"Input type is not supported: {input_type}"
        raise Exception(msg)

    s3_client = get_s3_client(region_name, session)
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

    return result_list
