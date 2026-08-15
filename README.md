<div align="center">

# ⚡ FastAPI Start Project

**A production-ready FastAPI starter with authentication, users, dynamic RBAC, auditing, logging, migrations and tests, all wired up out of the box.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-6BA81E)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#-license)

_Stop rewriting authentication, users, authorization and infrastructure on every new project. Clone this, configure your `.env`, and start building your domain._

</div>

---

## 📑 Table of Contents

- [Why this starter?](#-why-this-starter)
- [Features](#-features)
- [Tech stack](#-tech-stack)
- [Architecture](#-architecture)
- [RBAC design](#-rbac-design)
- [Project structure](#-project-structure)
- [Getting started](#-getting-started)
- [Environment variables](#-environment-variables)
- [Running with Docker](#-running-with-docker)
- [Database & migrations](#-database--migrations)
- [Creating the first admin](#-creating-the-first-admin)
- [API reference](#-api-reference)
- [Authentication flow](#-authentication-flow)
- [Running the tests](#-running-the-tests)
- [Using as a template](#-using-as-a-template)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 💡 Why this starter?

Every serious backend needs the same foundation:

- users
- authentication
- persisted sessions
- password recovery
- authorization
- auditing
- structured logging
- database migrations
- environment-based settings
- Docker support
- automated tests

Rebuilding all of that on each new project is a waste of time and easy to get wrong, especially from a security perspective.

**FastAPI Start Project** gives you that foundation already implemented, tested and following modern best practices, so you can jump straight to your business logic.

> 🎯 **Philosophy:** pragmatic modularity over heavy abstractions. Organized by feature, not by layer. Easy to read, easy to extend, easy to test and easy to replace when your domain needs something more specific.

---

## ✨ Features

### 🔐 Authentication & Security

- **JWT authentication** with access tokens
- **Refresh token rotation**, where old tokens are revoked on every refresh
- **Persisted sessions** through `UserSession`
- **Real logout**, terminating the persisted session and invalidating the access token immediately
- **Password hashing** with `bcrypt`
- **Refresh tokens stored as hashes** instead of plain text
- **Password reset tokens stored as hashes** instead of plain text
- **Password recovery flow** through `forgot-password` and `reset-password`
- **Single-use password reset tokens**
- **Expiring password reset tokens**
- **Current password verification** before password changes
- **Password reuse prevention**
- **Permission-based route protection** through RBAC guards

### 👤 User Management

- Public **registration**
- Public registration always creates users with the default `user` role
- **Current user profile** endpoint through `/users/me`
- Profile update fields:
  - `name`
  - `phone`
  - `avatar_url`
  - `job_title`
  - `bio`
- **Password change** with current-password verification
- **Self soft delete** through `/users/me`
- User status control through `is_active`
- Administrative user listing with pagination and filters
- Administrative user detail endpoint
- Administrative user creation
- Administrative user update
- Administrative soft delete
- Administrative hard delete
- Guardrails to prevent an administrator from deleting their own account

### 🛡️ Dynamic RBAC

The project includes a dynamic Role Based Access Control system.

The authorization model is:

```text
User
  ↓
Role
  ↓
Permissions
```

RBAC features include:

- Dynamic roles
- Dynamic permissions
- Role-to-permission assignment
- User-to-role assignment
- Built-in system roles
- Protected system roles
- Fine-grained administrative permissions
- Permission-based guards through `require_permission(...)`
- Role deletion safeguards
- Role assignment safeguards
- Administrative user responses with role and effective permissions
- Simplified API surface with fewer redundant endpoints

### 🧩 RBAC Granular Permissions

The RBAC module includes fine-grained administrative permissions:

| Permission | Purpose |
|-----------|---------|
| `roles.manage` | Manage roles and their permissions |
| `roles.users` | Assign roles to users |
| `roles.delete` | Delete roles |

This separation avoids giving excessive power to every administrator.

For example, a role may be allowed to manage role definitions and role permissions without being allowed to delete roles. Another role may be allowed to assign roles to users without being able to manage the RBAC catalog itself.

### 🛡️ Administration

Administrative capabilities include:

- Create users with a selected role
- List users with pagination and filters
- Get detailed user information
- Update users
- Soft delete users
- Hard delete users
- Assign roles to users
- List roles
- Create roles
- Update roles
- Delete roles with safeguards
- List permissions
- Assign permissions to roles
- Remove permissions from roles

### 📊 Observability

- **Audit logs** with:
  - `actor`
  - `target`
  - `action`
  - `resource`
  - `details`
- **Structured logging** across the application
- Service-level logging for critical operations such as user creation and authentication

### 🏗️ Infrastructure

- **Global exception handlers** for cleaner routers
- Semantic domain exceptions
- Alembic database migrations
- Docker and Docker Compose ready
- Pytest test suite covering critical flows
- Typed settings loaded from `.env` through `pydantic-settings`
- SQLite by default, easily swappable for PostgreSQL

---

## 🧰 Tech stack

| Layer | Technology |
|------|------------|
| Language | Python 3.13 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Validation | Pydantic v2 / pydantic-settings |
| Auth | python-jose (JWT) + bcrypt |
| Server | Uvicorn |
| Tests | Pytest + httpx |
| Containerization | Docker + Docker Compose |
| Default DB | SQLite, swappable for PostgreSQL |

---

## 🏛️ Architecture

The project follows a **feature-based modular architecture**.

Each feature module is a self-contained mini-application with its own:

```text
models
schemas
service
router
exceptions
```

Cross-cutting infrastructure lives under `core/`.

```text
┌──────────────────────────────────────────────────────────────┐
│ Routers                                                      │
│ Receive requests, call services, return responses             │
├──────────────────────────────────────────────────────────────┤
│ Schemas                                                      │
│ Validate input and shape output                              │
├──────────────────────────────────────────────────────────────┤
│ Services                                                     │
│ Business rules, orchestration, database operations            │
├──────────────────────────────────────────────────────────────┤
│ Models                                                       │
│ SQLAlchemy database mappings                                 │
└──────────────────────────────────────────────────────────────┘

Cross-cutting: config · database · security · logging · audit
```

### Architectural rule

Services should not know about HTTP.

They should raise semantic exceptions such as:

```python
UserNotFoundError
RoleNotFoundError
RoleInUseError
SystemRoleModificationError
PermissionAlreadyAssignedError
PermissionNotAssignedError
PermissionNotFoundError
```

Routers translate those exceptions into proper HTTP responses.

This keeps business logic reusable and easier to test.

---

## 🛡️ RBAC design

### Overview

The RBAC system is based on:

```text
User
  ↓
Role
  ↓
Permissions
```

Each user has exactly one role.

Each role can have zero or more permissions.

A permission is a specific capability, such as:

```text
users.list
roles.manage
roles.delete
```

Endpoints are protected with:

```python
require_permission(...)
```

This means access control is based on capabilities, not hardcoded role names.

---

### Why single-role RBAC?

The project intentionally uses a simple model:

```text
User → Role → Permissions
```

instead of:

```text
User → Roles → Permissions
```

This design was chosen because it is:

- easier to understand
- easier to test
- easier to document
- easier to maintain
- enough for most applications
- safer for a reusable starter project

A future project can evolve to multi-role users if the domain really needs it. The permission system itself does not need to be discarded for that migration.

---

### RBAC data model

#### User

Users are stored in:

```text
users
```

Important fields:

```text
id
name
email
password_hash
role_id
phone
avatar_url
job_title
bio
is_active
created_at
updated_at
```

The user references one role through:

```python
role_id
```

---

#### Role

Roles are stored in:

```text
roles
```

Important fields:

```text
id
name
description
is_system
created_at
```

Examples:

```text
admin
user
auditor
manager
operator
```

---

#### Permission

Permissions are stored in:

```text
permissions
```

Important fields:

```text
id
code
description
created_at
```

Examples:

```text
users.create
users.read
users.update
users.delete
users.list
roles.manage
roles.users
roles.delete
```

---

#### RolePermission

Role permissions are stored in:

```text
role_permissions
```

This table represents the many-to-many relationship between roles and permissions:

```text
Role
  ↕
Permissions
```

The association is explicit through a `RolePermissionModel`, rather than hidden only through a SQLAlchemy `secondary` relationship.

This makes future evolution easier if the project later needs metadata such as:

```text
granted_by
granted_at
expires_at
```

---

### Built-in roles

#### admin

The `admin` role is a system role.

It receives all permissions automatically.

Characteristics:

```text
is_system = True
```

Restrictions:

- cannot be deleted
- cannot be updated
- cannot receive permissions manually
- cannot lose permissions manually

Because the seed configuration grants `admin` all permissions, any new permission added to the central permission registry is automatically granted to `admin` when the RBAC seed runs.

---

#### user

The `user` role is the default role assigned during public registration.

Characteristics:

```text
is_system = True
```

Restrictions:

- cannot be deleted
- cannot be updated
- cannot receive permissions manually
- cannot lose permissions manually

By default, the `user` role has no administrative permissions.

---

### Permission registry

Permissions are centrally declared in code.

They follow this convention:

```text
resource.action
```

Current permissions include:

| Permission | Description |
|-----------|-------------|
| `users.create` | Create users |
| `users.read` | Read user details |
| `users.update` | Update users |
| `users.delete` | Delete users |
| `users.list` | List users |
| `roles.manage` | Manage roles and role permissions |
| `roles.users` | Assign roles to users |
| `roles.delete` | Delete roles |

This central registry is the source of truth for available application permissions.

---

### Administrative RBAC permissions

#### roles.manage

Allows managing the RBAC catalog.

This permission allows:

- list roles
- create roles
- update roles
- list permissions
- assign permissions to roles
- remove permissions from roles

This permission does not allow:

- deleting roles
- assigning roles to users

Those capabilities have their own permissions.

---

#### roles.users

Allows changing a user's role.

This permission exists because assigning roles to users is sensitive and should not automatically be granted to everyone who can manage role definitions.

This permission protects:

```http
PATCH /api/v1/admin/users/{user_id}/roles
```

---

#### roles.delete

Allows deleting roles.

This is considered a critical permission.

A user may be allowed to manage roles without being allowed to delete them.

This permission protects:

```http
DELETE /api/v1/admin/roles/{role_id}
```

---

### System role rules

System roles are protected framework roles.

Any role with:

```python
is_system = True
```

cannot be:

- updated
- deleted
- modified through permission assignment
- modified through permission removal

Attempts to modify system roles raise:

```python
SystemRoleModificationError
```

The API translates this into:

```http
400 Bad Request
```

---

### Role deletion rules

A role can be deleted only if all conditions are true:

```text
role.is_system is False
role is not assigned to any user
requesting user has roles.delete
```

If the role is assigned to one or more users, the service raises:

```python
RoleInUseError
```

The API returns:

```http
409 Conflict
```

Example response:

```json
{
  "detail": "Role is assigned to 3 users and cannot be deleted."
}
```

This avoids breaking referential integrity and prevents users from ending up with invalid role references.

The database also uses a restrictive foreign key from users to roles, which protects integrity at the persistence layer.

---

### User role assignment

User role assignment is handled through:

```http
PATCH /api/v1/admin/users/{user_id}/roles
```

This endpoint requires:

```text
roles.users
```

The endpoint validates:

- target user exists
- target role exists
- caller has permission to assign roles

It updates:

```python
user.role_id
```

The project intentionally does not use a `user_roles` association table because each user has exactly one role.

---

### Effective permissions

A user's effective permissions are derived from the user's role.

The model exposes helper properties and methods:

```python
user.role_name
```

Returns the current role name.

```python
user.permissions
```

Returns the list of permission codes granted through the user's role.

```python
user.has_permission("roles.delete")
```

Returns `True` or `False`.

These helpers centralize authorization logic in the domain model and avoid duplicating permission extraction code in multiple routers.

---

### Administrative user responses

Public and self-service user responses should stay focused on profile data.

Administrative user responses may include authorization information.

Administrative endpoints can expose:

```json
{
  "id": "...",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "auditor",
  "permissions": [
    "users.read",
    "users.list"
  ],
  "is_active": true
}
```

This avoids maintaining a separate RBAC inspection endpoint.

Instead of:

```http
GET /api/v1/admin/users/{user_id}/rbac
```

The API uses:

```http
GET /api/v1/admin/users/{user_id}
```

as the complete administrative user detail endpoint.

---

### Simplified RBAC API design

During development, some endpoints were intentionally removed to keep the API smaller and easier to maintain.

Removed as redundant:

```http
GET /api/v1/admin/roles/{role_id}
GET /api/v1/admin/roles/{role_id}/permissions
GET /api/v1/admin/users/{user_id}/rbac
```

The same information is available through:

```http
GET /api/v1/admin/roles
GET /api/v1/admin/users/{user_id}
```

This decision was made because real applications usually have a small number of roles, and returning role permissions together with roles is simpler than maintaining separate read endpoints.

Command endpoints were kept because they represent actions:

```http
POST   /api/v1/admin/roles/{role_id}/permissions/{permission_id}
DELETE /api/v1/admin/roles/{role_id}/permissions/{permission_id}
```

---

### RBAC endpoints

#### Roles

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `GET` | `/admin/roles` | `roles.manage` | List roles, including their permissions |
| `POST` | `/admin/roles` | `roles.manage` | Create a new non-system role |
| `PATCH` | `/admin/roles/{role_id}` | `roles.manage` | Update a non-system role |
| `DELETE` | `/admin/roles/{role_id}` | `roles.delete` | Delete a non-system, unused role |

#### Permissions

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `GET` | `/admin/permissions` | `roles.manage` | List all registered permissions |

#### Role permissions

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `POST` | `/admin/roles/{role_id}/permissions/{permission_id}` | `roles.manage` | Assign a permission to a role |
| `DELETE` | `/admin/roles/{role_id}/permissions/{permission_id}` | `roles.manage` | Remove a permission from a role |

#### User role assignment

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `PATCH` | `/admin/users/{user_id}/roles` | `roles.users` | Change the role assigned to a user |

---

## 📁 Project structure

```text
fastapi-start-project/
│
├── app/
│   ├── main.py                         # Application entry point
│   │
│   ├── core/                           # Cross-cutting infrastructure
│   │   ├── config.py                   # Typed settings (.env)
│   │   ├── database.py                 # Engine, SessionLocal, Base
│   │   ├── security.py                 # bcrypt + JWT
│   │   ├── logging.py                  # Structured logger
│   │   ├── exceptions.py               # Global exception handlers
│   │   └── dependencies/
│   │       └── database.py             # get_db dependency
│   │
│   ├── auth/                           # Authentication
│   │   ├── models.py                   # UserSession, RefreshToken, PasswordResetToken
│   │   ├── schemas.py
│   │   ├── service.py                  # login, refresh, logout, password reset
│   │   ├── router.py
│   │   ├── deps.py                     # CurrentUser, CurrentAdmin, CurrentSessionId
│   │   └── exceptions.py
│   │
│   ├── users/                          # Identity & user management
│   │   ├── models.py                   # UserModel, UserRole
│   │   ├── schemas.py                  # Public and admin user schemas
│   │   ├── service.py                  # User operations
│   │   ├── router.py                   # register, /users/me
│   │   ├── admin_router.py             # /admin/users
│   │   └── exceptions.py
│   │
│   ├── rbac/                           # Roles, permissions and authorization
│   │   ├── models.py                   # PermissionModel, RoleModel, RolePermissionModel
│   │   ├── schemas.py                  # Role and permission schemas
│   │   ├── service.py                  # Role lifecycle and user role assignment
│   │   ├── router.py                   # /admin/roles and /admin/permissions
│   │   ├── permissions.py              # Central permission registry
│   │   ├── role_permissions.py         # Role-permission service functions
│   │   ├── role_permissions_router.py  # Grant/revoke permissions from roles
│   │   ├── seed.py                     # Built-in roles and permissions seed
│   │   ├── exceptions.py               # RBAC domain exceptions
│   │   └── README.md                   # RBAC-specific documentation
│   │
│   └── audit/                          # Audit logs
│       ├── models.py
│       ├── service.py
│       └── constants.py
│
├── tests/                              # Pytest suite
│   ├── conftest.py                     # Shared fixtures
│   ├── auth/
│   ├── users/
│   │   ├── test_admin.py
│   │   ├── test_delete.py
│   │   ├── test_password_change.py
│   │   ├── test_profile.py
│   │   ├── test_register.py
│   │   └── test_user_detail.py
│   └── rbac/
│       ├── test_permissions.py
│       ├── test_role_deletion.py
│       ├── test_role_permissions.py
│       └── test_user_role_change.py
│
├── alembic/                            # Database migrations
├── scripts/
│   └── seed_admin.py                   # Creates the first admin
│
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 🚀 Getting started

### Prerequisites

- **Python 3.13**
- **pip**
- **venv**
- optional: **Docker Desktop**

### Installation

```bash
# 1. Get the project and enter the folder
cd my-project

# 2. Create and activate a virtual environment
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env

# 5. Generate a strong SECRET_KEY and paste it into .env
python -c "import secrets; print(secrets.token_hex(32))"

# 6. Apply database migrations
alembic upgrade head

# 7. Create the first admin user
python -m scripts.seed_admin

# 8. Run the development server
uvicorn app.main:app --reload
```

Now open:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## ⚙️ Environment variables

All configuration lives in `.env`.

Start from `.env.example`.

| Variable | Description | Default |
|---------|-------------|---------|
| `APP_NAME` | Application name shown in docs | `FastAPI Start Project` |
| `APP_DESCRIPTION` | Short description shown in docs | generic |
| `APP_VERSION` | API version | `1.0.0` |
| `APP_ENV` | Environment, such as `development` or `production` | `development` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT signing key, required and secret | none |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `60` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |

> 🔒 Never commit your `.env`. It contains the `SECRET_KEY`. If it leaks, anyone can forge tokens for any user.

### Switching to PostgreSQL

Change the connection string:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mydb
```

Then run:

```bash
alembic upgrade head
```

---

## 🐳 Running with Docker

```bash
# Build the image
docker compose build

# Start the container
docker compose up
```

The API will be available at:

[http://localhost:8000/docs](http://localhost:8000/docs)

The container name is derived from the project folder, so cloning this starter into a different folder renames it automatically.

---

## 🗄️ Database & migrations

This project uses **Alembic**.

You should not edit the schema manually.

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "describe your change"

# Apply pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# See migration history
alembic history

# See the current revision
alembic current
```

> 💡 If `--autogenerate` produces an empty migration, make sure the target database does not already contain the tables and that all models are imported in `alembic/env.py`.

---

## 🌱 Creating the first admin

Public registration always creates users with the default `user` role.

The first administrator must be created through the seed script:

```bash
python -m scripts.seed_admin
```

This solves the bootstrap problem.

After the first admin exists, users and roles can be managed through protected admin endpoints.

---

## 📚 API reference

All routes are prefixed with:

```text
/api/v1
```

---

## 🔓 Authentication

| Method | Endpoint | Auth | Description |
|-------|----------|------|-------------|
| `POST` | `/auth/register` | No | Register a new user with the default `user` role |
| `POST` | `/auth/login` | No | Authenticate and receive access and refresh tokens |
| `POST` | `/auth/refresh` | No | Rotate refresh token and receive a new token pair |
| `POST` | `/auth/logout` | Yes | Terminate the current session |
| `POST` | `/auth/forgot-password` | No | Request a password reset token |
| `POST` | `/auth/reset-password` | No | Reset password using a valid token |

---

## 👤 Users self-service

| Method | Endpoint | Auth | Description |
|-------|----------|------|-------------|
| `GET` | `/users/me` | Yes | Get authenticated user's profile |
| `PATCH` | `/users/me` | Yes | Update authenticated user's profile |
| `PATCH` | `/users/me/password` | Yes | Change authenticated user's password |
| `DELETE` | `/users/me` | Yes | Deactivate authenticated user's account |

---

## 🛡️ Admin users

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `POST` | `/admin/users/` | `users.create` | Create a user with a selected role |
| `GET` | `/admin/users/` | `users.list` | List users with pagination and filters |
| `GET` | `/admin/users/{user_id}` | `users.read` | Get complete administrative user details |
| `PATCH` | `/admin/users/{user_id}` | `users.update` | Update a user |
| `DELETE` | `/admin/users/{user_id}` | `users.delete` | Soft delete a user |
| `DELETE` | `/admin/users/{user_id}/hard` | `users.delete` | Permanently delete a user |
| `PATCH` | `/admin/users/{user_id}/roles` | `roles.users` | Change the user's role |

Administrative user responses may include:

```json
{
  "id": "...",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "auditor",
  "permissions": [
    "users.read",
    "users.list"
  ],
  "is_active": true
}
```

---

## 🛡️ RBAC

| Method | Endpoint | Permission | Description |
|-------|----------|------------|-------------|
| `GET` | `/admin/roles` | `roles.manage` | List roles with their permissions |
| `POST` | `/admin/roles` | `roles.manage` | Create a new role |
| `PATCH` | `/admin/roles/{role_id}` | `roles.manage` | Update a non-system role |
| `DELETE` | `/admin/roles/{role_id}` | `roles.delete` | Delete a non-system, unused role |
| `GET` | `/admin/permissions` | `roles.manage` | List all permissions |
| `POST` | `/admin/roles/{role_id}/permissions/{permission_id}` | `roles.manage` | Assign permission to role |
| `DELETE` | `/admin/roles/{role_id}/permissions/{permission_id}` | `roles.manage` | Remove permission from role |

---

## ❤️ Health

| Method | Endpoint | Auth | Description |
|-------|----------|------|-------------|
| `GET` | `/health` | No | Service status |

---

## 🔑 Authentication flow

```text
┌────────────┐   POST /auth/login    ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │
│            │ ◀──────────────────── │            │
└────────────┘  access + refresh     └────────────┘
      │
      │ Authorization: Bearer <access_token>
      ▼
┌────────────┐   protected requests  ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │
└────────────┘                       └────────────┘
      │
      │ access token expired?
      ▼
┌────────────┐  POST /auth/refresh   ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │
│            │ ◀──────────────────── │            │
└────────────┘  new access+refresh   └────────────┘
```

- Access tokens are short-lived.
- Refresh tokens are long-lived.
- Refresh token rotation revokes the previous token.
- Logout terminates the persisted session.
- Reusing an old refresh token is rejected.

> ℹ️ Swagger UI keeps the token only in memory. Refreshing the page logs you out there. A real frontend should handle token storage intentionally.

---

## 🧪 Running the tests

```bash
# Install test dependencies if needed
pip install pytest httpx

# Run the whole suite
pytest

# With coverage
pip install pytest-cov
pytest --cov=app
```

Tests use a dedicated SQLite database and recreate all tables before each test, guaranteeing isolation.

The production or development database is never touched.

Current suite status:

```text
68+ tests passing
```

Covered flows include:

### Authentication

- register
- login
- refresh token rotation
- logout
- password recovery
- reset password
- invalid credentials
- invalid tokens

### Users

- public registration
- current user profile
- profile update
- password change
- password reuse prevention
- self soft delete
- admin user creation
- admin user listing
- admin user detail
- admin user update
- admin soft delete
- admin hard delete
- self-delete guardrails

### RBAC

- permission guards
- built-in roles
- built-in permissions
- role creation
- role update
- role deletion
- role deletion protection when role is in use
- system role protection
- assigning permissions to roles
- removing permissions from roles
- duplicate permission assignment prevention
- missing permission validation
- user role assignment
- invalid user validation
- invalid role validation
- administrative user permission visibility

---

## 🧩 Using as a template

This repository is designed to be reused.

### Option A: GitHub Template

1. Push this project to GitHub.
2. Go to repository settings.
3. Enable **Template repository**.
4. For each new project, click **Use this template**.

This creates a fresh repository with no inherited commit history.

### Option B: Clone

```bash
git clone <your-repo-url> my-new-project
cd my-new-project
rm -rf .git && git init
cp .env.example .env
```

Then personalize:

```text
APP_NAME
DATABASE_URL
SECRET_KEY
```

After creating your project:

```bash
alembic upgrade head
python -m scripts.seed_admin
uvicorn app.main:app --reload
```

Start adding your own domain modules under `app/`, following the same pattern:

```text
models → schemas → service → router → exceptions
```

Examples:

```text
products
orders
invoices
notifications
documents
```

The starter foundation stays untouched. Your domain modules are added on top.

---

## 🗺️ Roadmap

Ideas for future iterations:

- [ ] PostgreSQL as the default database in Docker Compose
- [ ] GitHub Actions CI pipeline
- [ ] SMTP or external provider integration for password reset emails
- [ ] Rate limiting on authentication endpoints
- [ ] Active sessions management endpoint
- [ ] User-facing active sessions screen
- [ ] Audit trail for role changes
- [ ] Audit trail for permission changes
- [ ] Optional multi-role support
- [ ] Optional organization or tenant support
- [ ] Optional invite-based registration
- [ ] Optional email verification flow
- [ ] Optional admin dashboard frontend

---

## 📄 License

Released under the **MIT License**.

You can use it in personal and commercial projects.

---

<div align="center">

**Built with ❤️ and FastAPI.**

_If this starter saved you time, consider giving it a ⭐ on GitHub._

</div>
