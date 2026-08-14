"""Central registry of all permissions (source of truth in code)."""


class Permissions:
    """Permissions de Users"""
    USERS_CREATE = "users.create"
    USERS_READ = "users.read"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    USERS_LIST = "users.list"

    ROLES_MANAGE = "roles.manage"
    ROLES_DELETE = "roles.delete"
    ROLES_USERS = "roles.users"


ALL_PERMISSIONS: list[tuple[str, str]] = [
    (Permissions.USERS_CREATE, "Criar usuários"),
    (Permissions.USERS_READ, "Ver dados de usuários"),
    (Permissions.USERS_UPDATE, "Atualizar usuários"),
    (Permissions.USERS_DELETE, "Excluir usuários"),
    (Permissions.USERS_LIST, "Listar usuários"),
    (Permissions.ROLES_MANAGE, "Gerenciar roles e permissões"),
    (Permissions.ROLES_DELETE, "Excluir roles"),
    (Permissions.ROLES_USERS, "Atualizar as roles dos usuários"),
]

BUILTIN_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Administrador do sistema (acesso total)",
        "permissions": "*",
    },
    "user": {
        "description": "Usuário comum",
        "permissions": [],
    }
}
