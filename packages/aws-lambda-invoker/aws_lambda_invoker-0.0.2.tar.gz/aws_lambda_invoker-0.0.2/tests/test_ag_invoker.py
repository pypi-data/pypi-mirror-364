from aws_lambda_invoker import AGLambdaInvoker


def test_invoker():
    invoker = AGLambdaInvoker(
        lambda_name="TEST-LAMBDA",
        method="GET",
        path="TEST-path",
        body="TEST-body",
        headers={"key": "value"},
        query_params={"key": "value"},
        path_params={"key": "value"},
    )
    invoker.set_request_context("key", "value")
    assert type(invoker.get_request_id()) == str
    assert invoker.get_request_context("key") == "value"
