import logging
from datetime import datetime
from typing import List

from app.auth_client import AuthClient
from app.core.config import config
from app.core.context import Context
from app.core.exceptions import UserCreationError
from app.core.permissions import validate_permissions
from app.model.membership_model import UserMembership
from app.model.user_model import User
from app.service.membership_service import MembershipService
from app.utils.time import get_current_time


class UserService:
    def __init__(self):
        self.auth_client = AuthClient(config.aws_region)
        self.membership_service = MembershipService()

    def _build_user(self, **kwargs):
        current_time = get_current_time()
        return User(
            id=kwargs["id"],
            email=kwargs["email"],
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            memberships=kwargs["memberships"],
            created_at=kwargs.get("created_at", current_time),
            updated_at=kwargs.get("updated_at", current_time),
            deleted_at=kwargs.get("deleted_at", None),
        )

    def _rollback_user_creation(
        self, user_id: str, email: str, memberships: List[UserMembership]
    ):
        for membership in memberships:
            try:
                self.membership_service.delete_membership(
                    user_id, membership.location_id
                )
            except Exception as e:
                logging.error(
                    "Failed to delete membership during rollback",
                    extra={
                        "user_id": user_id,
                        "location_id": membership.location_id,
                        "error": str(e),
                    },
                )
        try:
            self.auth_client.admin_delete_user(email)
        except Exception as e:
            logging.error(
                "Failed to delete user during rollback",
                extra={"user_id": user_id, "error": str(e)},
            )

    def create_user(
        self,
        context: Context,
        email: str,
        first_name: str,
        last_name: str,
        memberships: List[UserMembership],
    ) -> User:
        # Verify that caller is allowed to create users for the requested locations
        for membership in memberships:
            validate_permissions(context.user_id, membership.location_id, "user:create")

        # Register user via auth client
        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "given_name", "Value": first_name},
            {"Name": "family_name", "Value": last_name},
        ]
        resp = self.auth_client.admin_create_user(
            username=email, user_attributes=user_attributes
        )

        created_user_id = resp.get("Username")
        created_at_time: datetime = resp.get("UserCreateDate")
        modified_at_time: datetime = resp.get("UserLastModifiedDate")
        if not created_user_id or not created_at_time or not modified_at_time:
            raise UserCreationError("Auth provider returned unexpected response")

        # Assign membership (locations and roles) to new user
        created_user_memberships: List[UserMembership] = []
        try:
            for membership in memberships:
                new_membership = self.membership_service.create_membership(
                    user_id=created_user_id,
                    location_id=membership.location_id,
                    roles=membership.roles,
                )
                created_user_memberships.append(
                    UserMembership(
                        location_id=new_membership.location_id,
                        roles=new_membership.roles,
                    )
                )
        except Exception as err:
            self._rollback_user_creation(
                user_id=created_user_id,
                email=email,
                memberships=created_user_memberships,
            )
            raise UserCreationError("Failed to assign memberships to user") from err

        user = self._build_user(
            id=created_user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            memberships=created_user_memberships,
            created_at=created_at_time.isoformat(),
            updated_at=modified_at_time.isoformat(),
        )
        return user
