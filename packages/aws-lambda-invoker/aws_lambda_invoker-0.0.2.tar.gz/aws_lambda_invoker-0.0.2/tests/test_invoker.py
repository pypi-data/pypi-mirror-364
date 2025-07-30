from unittest.mock import patch

from aws_lambda_invoker import LambdaInvoker, InvokeType


class PayloadResponse:
    @staticmethod
    def read():
        return b'{"status_code": 200, "body": "Hello World"}'


return_value = {"Payload": PayloadResponse()}


@patch.object(LambdaInvoker, "client_invoke", return_value=return_value)
def test_invoker(_):
    invoker = LambdaInvoker(
        lambda_name="TEST-LAMBDA",
        payload="{\"key\": \"value\"}",
        invoke_type=InvokeType.RequestResponse,
    )
    invoker.invoke()

    assert invoker.get_payload() == "{\"key\": \"value\"}"
    assert invoker.get_response_status_code() == return_value.get("status_code")
    assert invoker.get_response_body() == "Hello World"
