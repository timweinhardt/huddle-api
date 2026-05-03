import boto3
from botocore.exceptions import ClientError, BotoCoreError

from app.core.exceptions import DatabaseError


class Table:
    def __init__(self, table_name: str, aws_region: str):
        self.resource = boto3.resource("dynamodb", region_name=aws_region)
        self.table = self.resource.Table(table_name)

    def get_item(self, key: dict) -> dict:
        resp = self.table.get_item(Key=key)
        return resp.get("Item", {})

    def item_exists(self, key: dict) -> bool:
        item = self.get_item(key)
        if not item:
            return False
        return True

    def put_item(self, item: dict, condition_expression: str = None) -> dict:

        params = {"Item": item}
        if condition_expression:
            params["ConditionExpression"] = condition_expression

        try:
            response = self.table.put_item(**params)
        except ClientError as err:
            raise DatabaseError(f"DynamoDB client error: {str(err)}") from err
        except BotoCoreError as err:
            raise DatabaseError(f"AWS error: {str(err)}") from err
        return response

    def query(self, key_expression, filter_expression=None):
        try:
            if filter_expression:
                response = self.table.query(
                    KeyConditionExpression=key_expression,
                    FilterExpression=filter_expression,
                )
                return response.get("Items")
            response = self.table.query(
                KeyConditionExpression=key_expression,
            )
        except ClientError as err:
            raise DatabaseError(f"DynamoDB client error: {str(err)}") from err
        except BotoCoreError as err:
            raise DatabaseError(f"AWS error: {str(err)}") from err
        return response.get("Items", {})

    def query_gsi(self, index_name, key_expression, filter_expression=None):
        try:
            if filter_expression:
                return self.table.query(
                    IndexName=index_name,
                    KeyConditionExpression=key_expression,
                    FilterExpression=filter_expression,
                ).get("Items")
            response = self.table.query(
                IndexName=index_name,
                KeyConditionExpression=key_expression,
            )
        except ClientError as err:
            raise DatabaseError(f"DynamoDB client error: {str(err)}") from err
        except BotoCoreError as err:
            raise DatabaseError(f"AWS error: {str(err)}") from err
        return response.get("Items", {})

    def update_item(self, key, update_expression, attr_names, attr_values):
        resp = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
            ReturnValues="ALL_NEW",
        )
        return resp.get("Attributes", {})

    def delete_item(self, key: dict) -> dict:
        try:
            resp = self.table.delete_item(Key=key)
        except ClientError as err:
            raise DatabaseError(f"DynamoDB client error: {str(err)}") from err
        except BotoCoreError as err:
            raise DatabaseError(f"AWS error: {str(err)}") from err
        return resp
