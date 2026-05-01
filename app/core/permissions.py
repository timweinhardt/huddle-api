import yaml

from app.model.membership_model import Role

def load_permissions():
    with open("roles.yaml", "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader).get("roles")

permissions = load_permissions()

def user_has_permission(user_roles: set[Role], permission: str) -> bool:
    """Check if any of the user's roles grant the specified permission."""
    for role in user_roles:
        if permission in permissions.get(role, []):
            return True
    return False