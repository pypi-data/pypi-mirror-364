import logging
from enum import Enum

import boto3 as boto3
import orjson

logger = logging.getLogger(f"app.{__name__}")


class InvokeType(Enum):
    RequestResponse = "RequestResponse"
    Event = "Event"
    DryRun = "DryRun"


class LambdaInvoker:
    def __init__(self, lambda_name: str, payload: str, invoke_type: InvokeType = InvokeType.RequestResponse):
        """
        This method calls a lambda function

        Args:
            lambda_name: Name of the destination lambda function.
            payload: Payload for the request in JSON format.
            invoke_type: Type of invocation. RequestResponse, Event or DryRun. Default is RequestResponse.
        """
        self.response = None
        self.lambda_name = lambda_name
        self.payload = payload
        self.invoke_type = invoke_type

    def get_response(self) -> dict | str | None:
        return self.response

    def get_payload(self) -> str:
        return self.payload

    def get_response_body(self) -> dict | str | None:
        if self.response is None:
            return None
        elif isinstance(self.response, dict):
            return self.response.get("body")
        else:
            return self.response

    def get_response_status_code(self) -> int | None:
        return getattr(self.response, "status_code", None)

    def invoke(self) -> dict | str | None:
        """
        This method calls a lambda function.
        Returns: Response of the lambda function in JSON format if it can be decoded, else returns the response object.
        """

        logger.debug(
            "Payload Data",
            extra={
                "lambda_name": self.lambda_name,
                "invoke_type": self.invoke_type,
                "payload": self.payload,
            },
        )

        try:
            response = self.client_invoke()
        except Exception as e:
            logger.error(
                "Error invoking lambda function",
                extra={
                    "lambda_name": self.lambda_name,
                    "invoke_type": self.invoke_type,
                    "error": str(e),
                },
            )
            raise

        try:
            response_body = response["Payload"].read().decode("utf-8")
            self.response = orjson.loads(response_body)
        except orjson.JSONDecodeError:
            self.response = response

        logger.debug(
            "Response Data",
            extra={"lambda_name": self.lambda_name, "invoke_type": self.invoke_type, "response": self.response},
        )
        return self.response

    def client_invoke(self) -> dict:
        client = boto3.client("lambda")
        return client.invoke(
            FunctionName=self.lambda_name,
            InvocationType=self.invoke_type.value,
            Payload=self.payload,
        )
