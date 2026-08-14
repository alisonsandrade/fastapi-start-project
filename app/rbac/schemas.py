from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import field_validator


class PermissionResponse(BaseModel):
    id: str
    code: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    is_system: bool

    model_config = ConfigDict(from_attributes=True)


class RoleDetailResponse(RoleResponse):
    permissions: list[PermissionResponse] = Field(
        validation_alias="permission_items"
    )


class RoleCreateRequest(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Role name cannot be empty.")

        return value


class RoleUpdateRequest(BaseModel):
    description: str | None = None


"------------------------------------------------------------------------------"
"                           Permissions Schemas                                "
"------------------------------------------------------------------------------"


class PermissionResponseSchema(BaseModel):
    id: str
    code: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
