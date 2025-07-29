from typing import List
from models import Permission, Group


class GroupsPermissions:
    roles = []
    permissions = []

    def __init__(self, roles: List[str]) -> None:
        self.roles = [rol.replace('_role', '') for rol in list(
            set(roles)) if rol.endswith('_role')]
        self.permissions = [
            permission.replace('_permission', '') for permission in roles if permission.endswith('_permission')]

    def get_roles(self) -> List[Group]:
        roles_available = [Group(name=rol) for rol in self.roles]
        return roles_available

    def get_permissions(self) -> List[Permission]:
        permissions_available = [Permission(
            name=permission) for permission in self.permissions]
        return permissions_available

    def get_permissions_in_user(self) -> List[Permission]:
        return self.get_permissions()
