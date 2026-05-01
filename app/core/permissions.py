import yaml

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