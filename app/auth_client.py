import boto3

from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import config
from app.core.exceptions import AlreadyExistsError, AuthClientError


class AuthClient:
    def __init__(self, aws_region: str):
        self.client = boto3.client("cognito-idp", region_name=aws_region)
        self.user_pool_id = config.cognito_user_pool_id

    def admin_create_user(self, username, user_attributes):
        try:
            resp = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=user_attributes,
                ValidationData=[
                    {"Name": "string", "Value": "string"},
                ],
            )
            return resp.get("User", {})
        except ClientError as err:
            if err.response["Error"]["Code"] == "UsernameExistsException":
                raise AlreadyExistsError(
                    "A user with this username already exists"
                ) from err
            raise AuthClientError(f"Cognito client error: {str(err)}") from err
        except BotoCoreError as err:
            raise AuthClientError(f"AWS error: {str(err)}") from err

    def admin_delete_user(self, username):
        try:
            resp = self.client.admin_delete_user(
                UserPoolId=self.user_pool_id, Username=username
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "UsernameExistsException":
                raise AlreadyExistsError(
                    "A user with this username already exists"
                ) from err
            raise AuthClientError(f"Cognito client error: {str(err)}") from err
        except BotoCoreError as err:
            raise AuthClientError(f"AWS error: {str(err)}") from err
        return resp
