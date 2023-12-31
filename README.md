# skymantle-boto-buddy

A wrappper for boto3 to access common aws severless services primarily used for aws Lambda. The wrapper is dependent on using boto3 configuration using [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables) for setting credentials for accessing aws resources. It's also possible to provide a `boto3.Session` object for setting credentials.

When used within the context of an aws lambda function, no creditials are required and instances of boto3 resource and clients are created during lambda initialization.
The library determines its running in the context of a lambda function but looking for the `AWS_LAMBDA_FUNCTION_NAME` environment variable.


The following commands are supported:
- `make setup` - Installs all dependencies ands creates virtual environment
- `make unitTests` - runs unit tests
- `make lintAndAnalysis` - Runs [ruff](https://github.com/astral-sh/ruff), [bandit](https://github.com/PyCQA/bandit) and [black](https://github.com/psf/black)
- `make build` - Creates distribution