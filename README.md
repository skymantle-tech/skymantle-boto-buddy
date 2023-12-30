# skymantle-boto-buddy

A wrappper for boto3 to access common aws severless services primarily used for aws Lambda. The wrapper is dependent on using boto3 configuration using [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables) for setting credentials for accessing aws resources.

When used within the context of an aws lambda function, not creditials are required and instances of boto3 resource and clients are created during lambda initialization.