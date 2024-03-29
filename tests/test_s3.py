import os
from importlib import reload
from io import BytesIO

import boto3
import pytest
from boto3 import Session
from moto import mock_aws
from pytest_mock import MockerFixture

from skymantle_boto_buddy import EnableCache, s3


@pytest.fixture()
def environment(mocker: MockerFixture):
    return mocker.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "us-east-1", "AWS_LAMBDA_FUNCTION_NAME": "Test_Lambda_Function"},
    )


@mock_aws
def test_manual_region():
    reload(s3)

    client = s3.get_s3_client("ca-central-1")

    assert type(client).__name__ == "S3"


@mock_aws
def test_manual_session():
    reload(s3)

    client = s3.get_s3_client("ca-central-1", Session())

    assert type(client).__name__ == "S3"


@mock_aws
def test_s3_client_cache():
    reload(s3)

    s3_client_cached_one = s3.get_s3_client("ca-central-1", enable_cache=EnableCache.YES)
    s3_client_cached_two = s3.get_s3_client("ca-central-1", enable_cache=EnableCache.YES)

    assert s3_client_cached_one == s3_client_cached_two

    s3_client_no_cache_one = s3.get_s3_client("ca-central-1", enable_cache=EnableCache.NO)
    s3_client_no_cache_two = s3.get_s3_client("ca-central-1", enable_cache=EnableCache.NO)

    assert s3_client_no_cache_one != s3_client_no_cache_two
    assert s3_client_cached_one != s3_client_no_cache_one
    assert s3_client_cached_one != s3_client_no_cache_two


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_bucket():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    bucket = s3.get_bucket("some_bucket")
    bucket.put_object(Key="some_key", Body=b"File Data")

    response = s3_client.get_object(Bucket="some_bucket", Key="some_key")

    assert response["Body"].read() == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_object_signed_url():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b"File Data")

    url = s3.get_object_signed_url("some_bucket", "some_key")

    assert "https://s3.amazonaws.com/some_bucket/some_key?" in url
    assert "X-Amz-Algorithm" in url
    assert "X-Amz-Credential" in url
    assert "X-Amz-Date" in url
    assert "X-Amz-Expires" in url
    assert "X-Amz-SignedHeaders" in url
    assert "X-Amz-Signature" in url


@mock_aws
@pytest.mark.usefixtures("environment")
def test_put_object_signed_url():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    url = s3.put_object_signed_url("some_bucket", "some_key")

    assert "https://s3.amazonaws.com/some_bucket/some_key?" in url
    assert "X-Amz-Algorithm" in url
    assert "X-Amz-Credential" in url
    assert "X-Amz-Date" in url
    assert "X-Amz-Expires" in url
    assert "X-Amz-SignedHeaders" in url
    assert "X-Amz-Signature" in url


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_object():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b"File Data")

    response = s3.get_object("some_bucket", "some_key")

    assert response["Body"].read() == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_object_bytes():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b"File Data")

    data = s3.get_object_bytes("some_bucket", "some_key")

    assert data == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_object_json():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b'{"key": "value"}')

    data = s3.get_object_json("some_bucket", "some_key")

    assert data == {"key": "value"}


@mock_aws
@pytest.mark.usefixtures("environment")
def test_get_object_csv_reader():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b"col1,col2\ncol1value1,col2value2")

    csv_reader = s3.get_object_csv_reader("some_bucket", "some_key")
    data = list(csv_reader)

    assert data[0]["col1"] == "col1value1"
    assert data[0]["col2"] == "col2value2"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_upload_fileobj():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    s3.upload_fileobj("some_bucket", "some_key", BytesIO(b"File Data"))

    response = s3_client.get_object(Bucket="some_bucket", Key="some_key")

    assert response["Body"].read() == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_put_object():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    s3.put_object("some_bucket", "some_key", b"File Data")

    response = s3_client.get_object(Bucket="some_bucket", Key="some_key")

    assert response["Body"].read() == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_put_object_json():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    s3.put_object_json("some_bucket", "some_key", {"key": "value"})

    response = s3_client.get_object(Bucket="some_bucket", Key="some_key")

    assert response["Body"].read() == b'{"key": "value"}'


@mock_aws
@pytest.mark.usefixtures("environment")
def test_delete_object():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=b"File Data")

    s3.delete_object("some_bucket", "some_key")

    with pytest.raises(Exception) as e:
        s3_client.get_object(Bucket="some_bucket", Key="some_key")

    assert "The specified key does not exist." in str(e.value)


@mock_aws
@pytest.mark.usefixtures("environment")
def test_delete_objects_simplified():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key_1", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="some_key_2", Body=b"File Data")

    s3.delete_objects_simplified("some_bucket", ["some_key_1", "some_key_2"])

    with pytest.raises(Exception) as e:
        s3_client.get_object(Bucket="some_bucket", Key="some_key_1")

    assert "The specified key does not exist." in str(e.value)

    with pytest.raises(Exception) as e:
        s3_client.get_object(Bucket="some_bucket", Key="some_key_2")

    assert "The specified key does not exist." in str(e.value)


@mock_aws
@pytest.mark.usefixtures("environment")
def test_copy():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.create_bucket(Bucket="another_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key_1", Body=b"File Data")
    s3_client.create_bucket(Bucket="another_bucket")

    s3.copy("some_bucket", "some_key_1", "another_bucket", "some_key_2")

    response = s3_client.get_object(Bucket="another_bucket", Key="some_key_2")

    assert response["Body"].read() == b"File Data"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_list_objects_v2():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_1", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_2", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_3", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix2/some_key_4", Body=b"File Data")

    result = s3.list_objects_v2("some_bucket", "prefix1")
    assert len(result["keys"]) == 3

    assert result["keys"][0] == "prefix1/some_key_1"
    assert result["keys"][1] == "prefix1/some_key_2"
    assert result["keys"][2] == "prefix1/some_key_3"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_list_objects_v2_paging():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_1", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_2", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_3", Body=b"File Data")
    s3_client.put_object(Bucket="some_bucket", Key="prefix1/some_key_4", Body=b"File Data")

    result = s3.list_objects_v2("some_bucket", "prefix1", 2)
    assert len(result["keys"]) == 2
    assert result["keys"][0] == "prefix1/some_key_1"
    assert result["keys"][1] == "prefix1/some_key_2"

    assert len(result["NextContinuationToken"]) > 0

    result = s3.list_objects_v2("some_bucket", "prefix1", 2, result["NextContinuationToken"])

    assert len(result["keys"]) == 2
    assert result["keys"][0] == "prefix1/some_key_3"
    assert result["keys"][1] == "prefix1/some_key_4"


@mock_aws
@pytest.mark.usefixtures("environment")
def test_execute_sql_query_simplified():
    reload(s3)

    simple_csv = """a,b,c
    e,r,f
    y,u,i
    q,w,y"""

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")
    s3_client.put_object(Bucket="some_bucket", Key="some_key", Body=simple_csv)

    query = "SELECT count(*) FROM S3Object"

    data = s3.execute_sql_query_simplified("some_bucket", "some_key", query, "csv")

    assert data[0] == {"_1": 4}


@mock_aws
@pytest.mark.usefixtures("environment")
def test_execute_sql_query_simplified_invalid_input_type():
    reload(s3)

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket="some_bucket")

    query = "SELECT count(*) FROM S3Object"

    with pytest.raises(Exception) as e:
        s3.execute_sql_query_simplified("some_bucket", "some_key", query, "json")

    assert str(e.value) == "Input type is not supported: json"
