[![Status Checks](https://github.com/skymantle-tech/skymantle-boto-buddy/actions/workflows/status_checks.yml/badge.svg)](https://github.com/skymantle-tech/skymantle-boto-buddy/actions/workflows/status_checks.yml)

# Skymantle Boto Buddy

A wrapper for boto3 to access common aws serverless services primarily used for aws Lambda. By default the wrapper is dependent on using boto3 configuration through [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables) for setting credentials for accessing aws resources. It's also possible to provide a `boto3.Session` object for setting credentials.

When used within the context of an aws lambda function, no credentials are required and instances of boto3 resource and clients are created during lambda initialization when importing helpers. The library determines its running in the context of a lambda function but looking for the `AWS_LAMBDA_FUNCTION_NAME` environment variable.

The boto3 client and resource objects are cached but it is possible to also get uncached instances or cache can be disabled globally by setting the `BOTO_BUDDY_DISABLE_CACHE` environment variable. Supported values are `1`, `true`, `yes` and `on`.

## Installation
To install use:

```
pip3 install skymantle_boto_buddy
```

Using `skymantle_boto_buddy` will not include the boto3 dependency, useful when part of a lambda function and the lambda runtime version or a layer is used.  To include boto3 use:

```
pip3 install skymantle_boto_buddy[boto3]
```

## Usage

The library provides the following functions.

- Package
  - `get_boto3_client`
  - `get_boto3_resource`
- DynamoDb
  - `get_dynamodb_resource`
  - `get_table`
  - `put_item_simplified`
  - `update_item_simplified`
  - `get_item`
  - `delete_item`
  - `query`
  - `query_no_paging`
- S3
  - `get_s3_client`
  - `get_s3_resource`
  - `get_bucket`
  - `get_object_signed_url`
  - `put_object_signed_url`
  - `get_object`
  - `get_object_bytes`
  - `get_object_json`
  - `get_object_csv_reader`
  - `upload_fileobj`
  - `put_object`
  - `delete_object`
  - `delete_objects`
  - `copy`
  - `list_objects_v2`
  - `execute_sql_query_simplified`
- SSM
  - `get_ssm_client`
  - `get_parameter`
  - `get_parameter_decrypted`
- CloudFormation
  - `get_cloudformation_client`
  - `describe_stacks`
  - `get_stack_outputs`
- STS
  - `get_sts_client`
  - `get_caller_identity`
  - `get_caller_account`
- StepFunction
  - `get_stepfunction_client`
  - `start_execution`
  - `start_sync_execution`
  - `start_with_wait_for_completion`
  - `describe_execution`
- Logs
  - `get_logs_client`


### Examples

- running inside a lambda function or using environment variable credentials

```python
from skymantle_boto_buddy import dynamodb

dynamodb.put_item_simplified("table_name", {"PK": "some_key", "Description": "Some description"})
```

- providing a Session and specifying a profile named `developer`

```python
from boto3 import Session
from skymantle_boto_buddy import dynamodb

session = Session(profile_name="developer")
dynamodb.put_item_simplified("table_name", {"PK": "some_key", "Description": "Some description"}, session=session)
```

- Get a version of the s3 client that is not cached

```python
from boto3 import Session
from skymantle_boto_buddy import EnableCache, s3

s3_client = get_s3_client(enable_cache=EnableCache.NO)
```

- unit test a function with patching (also possible to use packages like [moto](https://github.com/getmoto/moto))

```python
# my_file.py
from skymantle_boto_buddy import dynamodb

def some_function():
  # ...
  item = dynamodb.get_item("table_name", {"PK": "some_key"})
  
  return item


# my_test.py
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
import my_file

@pytest.fixture()
def mock_dynamodb(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("my_file.dynamodb")
    return mock

def test_some_function(mock_dynamodb):
    mock_dynamodb.get_item.return_value = {"PK": "some_pk", "Name": "some value"}

    result = my_file.some_function()
    
    mock_dynamodb.get_item.assert_called_with("table_name", {"PK": "some_key"})
    assert result == {"PK": "some_pk", "Name": "some value"}
```

## Source Code Dev Notes

The following project commands are supported:
- `make clean` - Deletes virtual environment
- `make install` - Installs all dependencies and creates virtual environment
- `make unit_tests` - runs unit tests
- `make lint_and_analysis` - Runs [ruff](https://github.com/astral-sh/ruff), [bandit](https://github.com/PyCQA/bandit) and [black](https://github.com/psf/black)
- `make build` - Creates distribution