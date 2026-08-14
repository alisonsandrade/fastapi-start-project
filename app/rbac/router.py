from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies.database import Session, get_db
from app.deps import require_permission

from app.rbac import service
from app.rbac.exceptions import (
    RoleAlreadyExistsError,
    RoleNotFoundError,
    SystemRoleModificationError,
)
from app.rbac.models import PermissionModel, RoleModel
from app.rbac.permissions import Permissions
from app.rbac.schemas import (
    RoleCreateRequest,
    RoleResponse,
    RoleDetailResponse,
    PermissionResponse,
    RoleUpdateRequest,
)

router = APIRouter(
    prefix="/admin",
    tags=["RBAC"],
)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
)
def list_roles(
    db: Session = Depends(get_db)
) -> list[RoleModel]:
    return service.list_roles(db)


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
)
def list_permissions(
    db: Session = Depends(get_db)
) -> list[PermissionModel]:
    return service.list_permissions(db)


@router.get(
    "/roles/{role_id}",
    response_model=RoleDetailResponse,
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
)
def get_role(
    role_id: str,
    db: Session = Depends(get_db),
) -> RoleModel:
    role = service.get_role_by_id(db, role_id)

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )

    return role


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=201,
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE),
    )],
)
def create_role(
    payload: RoleCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        return service.create_role(
            db,
            name=payload.name,
            description=payload.description,
        )
    except RoleAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
)
def update_role(
    role_id: str,
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
) -> RoleModel:
    try:
        return service.update_role(
            db,
            role_id=role_id,
            description=payload.description,
        )
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
    except SystemRoleModificationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(
        require_permission(Permissions.ROLES_MANAGE)
    )],
)
def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        return service.delete_role(db, role_id)
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
    except SystemRoleModificationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
