import boto3

from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import config
from app.core.exceptions import AlreadyExistsError, AuthClientError, NotFoundError


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

    def admin_get_user_by_email(self, email: str):
        try:
            users = self.client.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'email = "{email}"',
            )
            if not users["Users"]:
                raise NotFoundError(f"User with email {email} not found")
            return users["Users"][0]
        except ClientError as err:
            if err.response["Error"]["Code"] == "UserNotFoundException":
                raise NotFoundError(f"User with email {email} not found") from err
            raise AuthClientError(f"Cognito client error: {str(err)}") from err
        except BotoCoreError as err:
            raise AuthClientError(f"AWS error: {str(err)}") from err

    def admin_update_user_attributes(self, username: str, user_attributes: list):
        try:
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=user_attributes,
            )

        except ClientError as err:
            if err.response["Error"]["Code"] == "AliasExistsException":
                raise AlreadyExistsError(
                    f"User with email {user_attributes[0]['Value']} already exists"
                ) from err
            raise AuthClientError(f"Cognito client error: {str(err)}") from err
        except BotoCoreError as err:
            raise AuthClientError(f"AWS error: {str(err)}") from err

    def list_users(self):
        users = []
        pagination_token = None

        while True:
            kwargs = {"UserPoolId": self.user_pool_id}
            if pagination_token:
                kwargs["PaginationToken"] = pagination_token

            try:
                response = self.client.list_users(**kwargs)
            except ClientError as err:
                raise AuthClientError(f"Cognito client error: {str(err)}") from err
            except BotoCoreError as err:
                raise AuthClientError(f"AWS error: {str(err)}") from err

            users.extend(response["Users"])

            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break

        return users
