# Skymantle Boto Buddy

A wrappper for boto3 to access common aws severless services primarily used for aws Lambda. The wrapper is dependent on using boto3 configuration using [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables) for setting credentials for accessing aws resources. It's also possible to provide a `boto3.Session` object for setting credentials.

When used within the context of an aws lambda function, no creditials are required and instances of boto3 resource and clients are created during lambda initialization.
The library determines its running in the context of a lambda function but looking for the `AWS_LAMBDA_FUNCTION_NAME` environment variable.

The boto3 client and resource objects are cached but it is possible to also get uncached instances or cache can be disabled globally by setting the `BOTO_BUDDY_DISABLE_CACHE` environment variable. Supported values are `1`, `true`, `yes` and `on`.

The following project commands are supported:
- `make setup` - Installs all dependencies ands creates virtual environment
- `make unitTests` - runs unit tests
- `make lintAndAnalysis` - Runs [ruff](https://github.com/astral-sh/ruff), [bandit](https://github.com/PyCQA/bandit) and [black](https://github.com/psf/black)
- `make build` - Creates distribution

## Installation

Currently the package isn't on pypi, however the GitHub repo can be referenced directly in a requirements file.  For example:
- `skymantle_boto_buddy @ git+https://github.com/skymantle-tech/skymantle-boto-buddy@main`

Using `skymantle_boto_buddy` will not include the boto3 dependency, useful when part of a lambda function and the lambda runtime version of boto3 or a layer is used.  To include boto3 use `skymantle_boto_buddy[boto3]`.

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


### Examples

- running inside a lambda function or using environment variable creditional

```python
from skymantle_boto_buddy import dynamodb

dynamodb.put_item_simplified("table_name", {"PK": "some_key", "Description": "Some description"})
```

- providing a Session and specifiying a profile named `developer`

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