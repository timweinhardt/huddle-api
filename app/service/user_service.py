from datetime import datetime
import logging
import time
from typing import List, Optional

from app.auth_client import AuthClient
from app.core.config import config
from app.core.context import Context
from app.core.exceptions import PermissionDeniedError, UserCreationError
from app.core.permissions import validate_permissions
from app.model.membership_model import UserMembership
from app.model.user_model import User, UploadProfilePictureResp
from app.s3 import upload_image_to_s3
from app.service.membership_service import MembershipService
from app.utils.time import get_current_time, serialize_time
from app.utils.image import parse_base64_image


class UserService:
    def __init__(self):
        self.auth_client = AuthClient(config.aws_region)
        self.membership_service = MembershipService()

    @staticmethod
    def _build_user(**kwargs):
        current_time = get_current_time()
        return User(
            id=kwargs["id"],
            email=kwargs["email"],
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"],
            memberships=kwargs["memberships"],
            created_at=kwargs.get("created_at", current_time),
            updated_at=kwargs.get("updated_at", current_time),
            is_active=True,
            is_confirmed=False,
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

    @staticmethod
    def _get_user_attr(attributes: list, name: str) -> Optional[str]:
        return next(
            (attr["Value"] for attr in attributes if attr["Name"] == name),
            None,
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
            created_at=serialize_time(created_at_time),
            updated_at=serialize_time(created_at_time),
        )
        return user

    def update_user(
        self,
        context: Context,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        picture_url: Optional[str] = None,
    ) -> None:
        common_location_membership = (
            self.membership_service.get_common_location_membership(
                context.user_id, user_id
            )
        )
        if common_location_membership is None:
            raise PermissionDeniedError("You are not authorized to update this user")
        validate_permissions(context.user_id, common_location_membership, "user:update")
        self.update_cognito_user_attributes(
            user_id, email=email, first_name=first_name, last_name=last_name, picture=picture_url
        )

    def upload_profile_picture(
        self,
        context: Context,
        user_id: str,
        base64: Optional[str] = None,
        extension: Optional[str] = None,
    ) -> UploadProfilePictureResp:
        is_owner = context.user_id == user_id
        common_location_membership = (
            self.membership_service.get_common_location_membership(
                context.user_id, user_id
            )
        )
        if common_location_membership is None:
            raise PermissionDeniedError("You are not authorized to update this user")

        validate_permissions(
            context.user_id, common_location_membership, "user:update", is_owner
        )

        picture_url = None
        if base64 is not None:
            image_data, content_type = parse_base64_image(base64)
            picture_filename = f"users/{user_id}/picture"
            if extension is not None:
                picture_filename += f".{extension}"

            picture_url = upload_image_to_s3(
                image_data,
                content_type,
                config.s3_bucket_name,
                picture_filename,
                config.aws_region,
            )

        picture_url = f"{picture_url}#t={int(time.time())}"

        return UploadProfilePictureResp(picture_url=picture_url)

    def update_cognito_user_attributes(
        self,
        username: str,
        *,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> None:
        user_attributes: List[dict] = []
        if email is not None:
            user_attributes.append({"Name": "email", "Value": email})
        if first_name is not None:
            user_attributes.append({"Name": "given_name", "Value": first_name})
        if last_name is not None:
            user_attributes.append({"Name": "family_name", "Value": last_name})
        if picture is not None:
            user_attributes.append({"Name": "picture", "Value": picture})
        if not user_attributes:
            raise ValueError(
                "At least one of email, first_name, last_name, picture must be provided"
            )

        self.auth_client.admin_update_user_attributes(username, user_attributes)

    def get_location_users(self, context: Context, location_id: str) -> List[User]:
        validate_permissions(context.user_id, location_id, "user:read")

        auth_users = self.auth_client.list_users()

        location_memberships = self.membership_service.get_location_memberships(
            location_id
        )

        users: List[User] = []

        for membership in location_memberships:
            user_details = next(
                (u for u in auth_users if u["Username"] == membership.user_id), None
            )

            if not user_details:
                logging.warning(
                    "Skipping user %s: user not found from auth client",
                    membership.user_id,
                )
                continue

            try:
                attributes = user_details.get("Attributes", [])
                user_id = user_details["Username"]

                email = self._get_user_attr(attributes, "email")
                first_name = self._get_user_attr(attributes, "given_name")
                last_name = self._get_user_attr(attributes, "family_name")
                avatar_url = self._get_user_attr(attributes, "picture")

                if not all([email, first_name, last_name]):
                    logging.warning(
                        "Skipping user %s: missing required attributes", user_id
                    )
                    continue

                created_at = serialize_time(user_details.get("UserCreateDate"))
                updated_at = serialize_time(user_details.get("UserLastModifiedDate"))
                is_active = user_details.get("Enabled")
                is_confirmed = user_details.get("UserStatus") == "CONFIRMED"

                user_memberships = self.membership_service.get_user_memberships(user_id)

                users.append(
                    User(
                        id=user_id,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        avatar_url=avatar_url,
                        memberships=user_memberships,
                        created_at=created_at,
                        updated_at=updated_at,
                        is_active=is_active,
                        is_confirmed=is_confirmed,
                    )
                )

            except Exception as err:
                logging.warning(
                    "Skipping user %s: unexpected error during hydration %s",
                    user_details.get("Username"),
                    err,
                )
                continue

        return users
