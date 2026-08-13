"""Central registry of all permissions (source of truth in code)."""
class Permissions:
    #Users
    USERS_CREATE = "users.create"
    USERS_READ = "users.read"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    USERS_LIST = "users.list"


ALL_PERMISSIONS: list[tuple[str, str]] = [
    (Permissions.USERS_CREATE, "Criar usuários"),
    (Permissions.USERS_READ, "Ver dados de usuários"),
    (Permissions.USERS_UPDATE, "Atualizar usuários"),
    (Permissions.USERS_DELETE, "Excluir usuários"),
    (Permissions.USERS_LIST, "Listar usuários"),
]

BUILTIN_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Administrador do sistema (acesso total)",
        "permissions": "*",
    },
    "member": {
        "description": "Usuário comum",
        "permissions": [],
    }
}
