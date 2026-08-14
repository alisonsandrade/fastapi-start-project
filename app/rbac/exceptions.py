class RoleNotFoundError(Exception):
    pass


class RoleAlreadyExistsError(Exception):
    pass


class SystemRoleModificationError(Exception):
    pass


class RoleInUseError(Exception):
    pass


class PermissionNotFoundError(Exception):
    pass


class PermissionAlreadyAssignedError(Exception):
    pass


class PermissionNotAssignedError(Exception):
    pass
