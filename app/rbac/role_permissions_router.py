from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from app.core.dependencies.database import get_db
from app.deps import require_permission

from app.rbac.exceptions import (
    PermissionAlreadyAssignedError,
    PermissionNotAssignedError,
    PermissionNotFoundError,
    RoleNotFoundError,
    SystemRoleModificationError,
)
from app.rbac.permissions import Permissions
from app.rbac.role_permissions import (
    add_permission_to_role,
    list_role_permissions,
    remove_permission_from_role,
)
from app.rbac.schemas import PermissionResponseSchema


router = APIRouter(
    prefix="/admin/roles",
    tags=["Role Permissions"]
)


@router.get(
    "/{roles_id}/permissions",
    response_model=list[PermissionResponseSchema],
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
    summary="List role permissions.",
)
def get_role_permissions(
    role_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return list_role_permissions(db, role_id)
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{role_id}/permissions/{permission_id}",
    dependencies=[
        Depends(
            require_permission(
                Permissions.ROLES_MANAGE
            )
        )
    ],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign permission to role",
)
def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        add_permission_to_role(
            db,
            role_id,
            permission_id,
        )
    except (RoleNotFoundError, PermissionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except PermissionAlreadyAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except SystemRoleModificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    dependencies=[
        Depends(
            require_permission(
                Permissions.ROLES_MANAGE
            )
        )
    ],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove permission from role",
)
def unassign_permission_from_role(
    role_id: str,
    permission_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        remove_permission_from_role(
            db,
            role_id,
            permission_id,
        )
    except (RoleNotFoundError, PermissionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except PermissionNotAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except SystemRoleModificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
