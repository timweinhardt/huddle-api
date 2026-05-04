import yaml

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.service.membership_service import MembershipService


def load_permissions():
    with open("app/roles.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("roles", {})


role_permissions = load_permissions()


def parse_permission_string(permission: str):
    permission_parts = permission.split(":")
    resource = permission_parts[0]
    action = None
    scope = "any"

    if len(permission_parts) > 1:
        action = permission_parts[1]
    if len(permission_parts) > 2:
        scope = permission_parts[2]

    return resource, action, scope


def user_has_permission(
    user_roles: set[str],
    required_permission: str,
    is_owner: bool = False,
) -> bool:
    """
    Check if a user has a required permission.
    """
    required_resource, required_action, _ = parse_permission_string(required_permission)

    for role in user_roles:
        permissions = role_permissions.get(role, [])

        for permission in permissions:
            resource, action, scope = parse_permission_string(permission)

            if resource == required_resource and action == required_action:
                if scope == "any":
                    return True

                if scope == "own" and is_owner:
                    return True
    return False


def validate_permissions(
    user_id: str, location_id: str, permission_string: str, is_owner: bool = False
) -> None:
    # Verify permissions at the location level
    try:
        membership = MembershipService().get_membership(
            user_id=user_id, location_id=location_id
        )
    except NotFoundError as err:
        raise PermissionDeniedError(
            "Insufficient permissions for this location"
        ) from err

    # Verify permissions at the role level
    if not user_has_permission(
        user_roles=membership.roles,
        required_permission=permission_string,
        is_owner=is_owner,
    ):
        raise PermissionDeniedError(
            f"Insufficient permissions for this role, missing {permission_string}"
        )
