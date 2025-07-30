import copy
import uuid
from enum import Enum

import orjson

from .lambda_invoker import LambdaInvoker, InvokeType


class AGLambdaInvoker(LambdaInvoker):
    """
    This class is a wrapper for LambdaInvoker class. It is used to call a lambda function as an API Gateway would do.
    https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    """

    BASE_PAYLOAD: dict = {
        "httpMethod": None,
        "path": None,
        "body": "{}",  # This value is like None to Lambda. BUT IT CANNOT BE NONE
        "resource": "/{proxy+}",
        "isBase64Encoded": False,
        "headers": {},
        "queryStringParameters": None,
        "pathParameters": None,
        "requestContext": {
            "httpMethod": None,
            "requestId": None,
            "authorizer": {"claims": {}},
            "identity": {
                "sourceIp": "0.0.0.0",  # This value will not be replaced by the real value, but it is not necessary
            },
        },
    }

    class Methods(Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        OPTIONS = "OPTIONS"
        HEAD = "HEAD"

    @staticmethod
    def generate_request_id() -> str:
        return str(uuid.uuid4())

    def __init__(
            self,
            lambda_name: str,
            method: str | Methods,
            path: str,
            body: str | None = None,
            headers: dict | None = None,
            query_params: dict | None = None,
            path_params: dict | None = None,
    ) -> None:
        """
        This method calls a lambda function as an API Gateway would do.

        Args:
            lambda_name: Name of the destination lambda function.
            method: Method of the request.
            path: Path of the request.
            body: Body of the request in JSON format.
            headers: Headers of the request.
            query_params: Query parameters.
            path_params: Path parameters.

        Returns: Response of the lambda function in JSON format if can be decoded, else returns the response object.
        """
        if isinstance(method, str):
            method = self.Methods(method.upper())

        if path is None:
            raise ValueError("Invalid path")

        self.payload_dict: dict = copy.deepcopy(self.BASE_PAYLOAD)

        self.payload_dict["httpMethod"] = method.value
        self.payload_dict["path"] = path
        self.payload_dict["body"] = body
        self.payload_dict["headers"] = headers
        self.payload_dict["queryStringParameters"] = query_params
        self.payload_dict["pathParameters"] = path_params
        self.payload_dict["requestContext"]["requestId"] = self.generate_request_id()
        self.payload_dict["requestContext"]["httpMethod"] = self.payload_dict["httpMethod"]

        super().__init__(lambda_name, orjson.dumps(self.payload_dict).decode("utf-8"), InvokeType.RequestResponse)

    def set_request_context(self, key: str, value: str) -> None:
        self.payload_dict["requestContext"][key] = value
        self.payload = orjson.dumps(self.payload_dict).decode("utf-8")

    def get_request_context(self, key: str) -> str:
        return self.payload_dict["requestContext"].get(key)

    def get_request_id(self) -> str:
        return self.payload_dict["requestContext"]["requestId"]
