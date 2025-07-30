# AWS Lambda invoker

Simple package for lambda invocation with AWS boto3.
This package is intended to be used as an interface for invoking AWS Lambda functions emulating AWS API Gateway, SNS, Event bridge and SQS.

## Installation

```console
$ pip install aws-lambda-invoker
```


## Example

```python
invoker = LambdaInvoker(
    lambda_name="TEST-LAMBDA",
    payload="{\"key\": \"value\"}",
    invoke_type=InvokeType.RequestResponse,
)
response = invoker.invoke()

# or using AGLambdaInvoker

invoker = AGLambdaInvoker(
    lambda_name="TEST-LAMBDA",
    method="GET",
    path="TEST-path",
    body="TEST-body",
    headers={"key": "value"},
    query_params={"key": "value"},
    path_params={"key": "value"},
)
response = invoker.invoke()
```
