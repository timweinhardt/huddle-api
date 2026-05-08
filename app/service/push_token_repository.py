from typing import List
from boto3.dynamodb.conditions import Key

from app.core.config import config
from app.db import Table


class ExponentPushTokenRepository:
    def __init__(self):
        self.db = Table(
            table_name=f"{config.environment}-huddle-exponent-push-tokens",
            aws_region=config.aws_region,
        )

    def register_token(self, user_id: str, push_token: str):
        item = {
            "user_id": user_id,
            "push_token": push_token,
        }
        self.db.put_item(item=item)

    def get_tokens_for_user(self, user_id: str) -> List[str]:
        key_expression = Key("user_id").eq(user_id)
        items = self.db.query(key_expression=key_expression) or []
        return [item["push_token"] for item in items if "push_token" in item]

    def deactivate_token(self, push_token: str) -> None:
        # Look up by GSI `push_token-index`, then delete matching items
        key_expression = Key("push_token").eq(push_token)
        items = (
            self.db.query_gsi(
                index_name="push_token-index",
                key_expression=key_expression,
            )
            or []
        )

        for item in items:
            user_id = item["user_id"]
            pk = {"user_id": user_id, "push_token": push_token}
            self.db.delete_item(pk)
