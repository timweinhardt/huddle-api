import boto3

class Table:
    def __init__(self, table_name: str, aws_region: str):
        self.resource = boto3.resource('dynamodb', region_name=aws_region)
        self.table = self.resource.Table(table_name)

    def get_item(self, key: dict) -> dict:
        resp = self.table.get_item(
            Key=key
        )
        return resp.get("Item", {})