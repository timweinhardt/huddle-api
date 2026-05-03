import yaml

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.service.membership_service import MembershipService

def load_permissions():
    with open("roles.yaml", "r") as f:
        return yaml.safe_load(f).get("roles", {})

role_permissions = load_permissions()

def user_has_permission(
    user_roles: set[str],
    required_permissions: set[str],
    require_all: bool = False
) -> bool:
    """
    Check permissions for a user.
    """

    user_permissions = set()
    for role in user_roles:
        user_permissions.update(role_permissions.get(role, []))

    if require_all:
        return required_permissions.issubset(user_permissions)
    else:
        return bool(user_permissions & required_permissions)
    
def validate_permissions(
        user_id: str,
        location_id: str,
        permission_string: str,
        is_owner: bool = False
    ) -> None:
    # Verify permissions at the location level
    try:
        membership = MembershipService().get_membership(user_id=user_id, location_id=location_id)
    except NotFoundError:
        raise PermissionDeniedError("Insufficient permissions for this location")
    
    # Verify permissions at the role level
    if is_owner:
        if not user_has_permission(membership.roles, {
            permission_string,
            f"{permission_string}:own",
            f"{permission_string}:any"
        }, require_all=False):
            raise PermissionDeniedError("Insufficient permissions for this role")
    else:
        if not user_has_permission(membership.roles, {
            permission_string,
            f"{permission_string}:any"
        }, require_all=False):
            raise PermissionDeniedError("Insufficient permissions for this role")