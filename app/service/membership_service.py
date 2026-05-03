from typing import List
from boto3.dynamodb.conditions import Key

from app.core.config import config
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.db import Table
from app.model.membership_model import (
    LocationMembership,
    Membership,
    Role,
    UserMembership,
)
from app.utils.time import get_current_time


class MembershipService:
    def __init__(self):
        self.db = Table(
            table_name=config.memberships_table_name, aws_region=config.aws_region
        )

    def _build_membership(self, **kwargs) -> dict:
        current_time = get_current_time()
        return {
            "user_id": kwargs["user_id"],
            "location_id": kwargs["location_id"],
            "user_key": f"USER#{kwargs['user_id']}",
            "location_key": f"LOCATION#{kwargs['location_id']}",
            "location_index_key": f"LOCATION#{kwargs['location_id']}",
            "user_index_key": f"USER#{kwargs['user_id']}",
            "roles": kwargs["roles"],
            "created_at": kwargs.get("created_at", current_time),
            "updated_at": kwargs.get("updated_at", current_time),
        }

    def _get_membership_key(self, user_id: str, location_id: str) -> dict:
        return {
            "user_key": f"USER#{user_id}",
            "location_key": f"LOCATION#{location_id}",
        }

    def create_membership(
        self, user_id: str, location_id: str, roles: set[Role]
    ) -> Membership:
        membership_item = self._build_membership(
            user_id=user_id, location_id=location_id, roles=roles
        )
        # Check if membership exists
        key = self._get_membership_key(user_id, location_id)
        if self.db.item_exists(key):
            raise AlreadyExistsError("Membership already exists")

        self.db.put_item(item=membership_item)
        return Membership.model_validate(membership_item)

    def get_membership(self, user_id: str, location_id: str) -> Membership:
        key = self._get_membership_key(user_id, location_id)
        item = self.db.get_item(key)
        if not item:
            raise NotFoundError("Membership not found")
        return Membership.model_validate(item)

    def update_membership_roles(
        self, user_id: str, location_id: str, roles: set[Role]
    ) -> Membership:
        # Check if membership exists
        key = self._get_membership_key(user_id, location_id)
        item = self.db.get_item(key)
        if not item:
            raise NotFoundError("Membership not found")

        # Return early if no attributes are changed
        if item.get("roles") == roles:
            return Membership.model_validate(item)

        update_expression = "SET #roles = :roles, #updated_at = :updated_at"
        names = {"#roles": "roles", "#updated_at": "updated_at"}
        values = {":roles": roles, ":updated_at": get_current_time()}

        updated_item = self.db.update_item(
            key=key,
            update_expression=update_expression,
            attr_names=names,
            attr_values=values,
        )
        return Membership.model_validate(updated_item)

    def delete_membership(self, user_id: str, location_id: str) -> None:
        key = self._get_membership_key(user_id, location_id)
        item = self.db.get_item(key)
        if not item:
            raise NotFoundError("Membership not found")
        self.db.delete_item(key)

    def get_user_memberships(
        self,
        user_id: str,
    ) -> List[UserMembership]:
        key_expression = Key("user_key").eq(f"USER#{user_id}")
        items = self.db.query(key_expression=key_expression)
        return [UserMembership.model_validate(membership) for membership in items]

    def get_location_memberships(
        self,
        location_id: str,
    ) -> List[LocationMembership]:
        key_expression = Key("location_index_key").eq(f"LOCATION#{location_id}")
        items = self.db.query_gsi(
            index_name="location_membership_index", key_expression=key_expression
        )
        return [LocationMembership.model_validate(membership) for membership in items]

    def is_member(self, user_id: str, location_id: str) -> bool:
        key = self._get_membership_key(user_id, location_id)
        return self.db.item_exists(key)
