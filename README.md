<div align="center">

# ⚡ FastAPI Start Project

**A production-ready FastAPI starter — authentication, users, auditing, logging, migrations and tests, all wired up out of the box.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-6BA81E)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#-license)

_Stop rewriting authentication, users and infrastructure on every new project. Clone this, configure your `.env`, and start building your domain._

</div>

---

## 📑 Table of Contents

- [Why this starter?](#-why-this-starter)
- [Features](#-features)
- [Tech stack](#-tech-stack)
- [Architecture](#-architecture)
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

Every serious backend needs the same foundation: users, authentication, sessions,
password recovery, auditing, logging, migrations, containerization and tests.

Rebuilding all of that on each new project is a waste of time — and easy to get
wrong (security-wise).

**FastAPI Start Project** gives you that foundation already implemented, tested
and following modern best practices, so you can jump straight to your business
logic.

> 🎯 **Philosophy:** pragmatic modularity over heavy abstractions. Organized by
> feature, not by layer. Easy to read, easy to extend.

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT authentication** with access tokens
- **Refresh token rotation** — old tokens are revoked on every refresh
- **Persisted sessions** (`UserSession`) — enables real logout and future "active sessions" screens
- **Real logout** — terminates the session and invalidates the access token immediately
- **Password hashing** with `bcrypt`
- **Refresh / reset tokens** stored as **SHA-256 hashes** (never in plain text)
- **Password recovery flow** (`forgot-password` / `reset-password`) with single-use, expiring tokens

### 👤 User Management
- Public **registration** (always creates `MEMBER` role)
- **Profile** read & update (`name`, `phone`, `avatar_url`, `job_title`, `bio`)
- **Password change** with current-password verification and reuse prevention
- **Soft delete** (deactivate) and **hard delete** (permanent) of accounts
- **Role-based access control** (`ADMIN` / `MEMBER`)

### 🛡️ Admin
- Create users with any role
- List users (with pagination & filters)
- Update users
- Soft delete / hard delete any user
- Guardrails: an admin **cannot delete their own account**

### 📊 Observability
- **Audit logs** with `actor`, `target`, `action`, `resource` and `details`
- **Structured logging** across the application

### 🏗️ Infrastructure
- **Global exception handlers** — clean routers, no repetitive `try/except`
- **Alembic** database migrations
- **Docker & Docker Compose** ready
- **Pytest** test suite covering all critical flows
- **Typed settings** loaded from `.env` (pydantic-settings)

---

## 🧰 Tech stack

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Language         | Python 3.13                         |
| Web framework    | FastAPI                             |
| ORM              | SQLAlchemy 2.0                      |
| Migrations       | Alembic                             |
| Validation       | Pydantic v2 / pydantic-settings     |
| Auth             | python-jose (JWT) + bcrypt          |
| Server           | Uvicorn                             |
| Tests            | Pytest + httpx                      |
| Containerization | Docker + Docker Compose             |
| Default DB       | SQLite (swappable for PostgreSQL)   |

---

## 🏛️ Architecture

The project follows a **feature-based modular architecture**. Each module is a
self-contained mini-app (`models`, `schemas`, `service`, `router`, `exceptions`),
while cross-cutting infrastructure lives under `core/`.

```
┌─────────────────────────────────────────────────────────┐
│  Routers (HTTP)        → receive requests, return responses │
├─────────────────────────────────────────────────────────┤
│  Schemas (Pydantic)    → validate input / shape output      │
├─────────────────────────────────────────────────────────┤
│  Services (business)   → rules, orchestration               │
├─────────────────────────────────────────────────────────┤
│  Models (SQLAlchemy)   → database tables                    │
└─────────────────────────────────────────────────────────┘
        Cross-cutting: config · database · security · logging · audit
```

**Golden rule:** services never know about HTTP. They raise semantic exceptions;
global handlers translate them into proper HTTP status codes.

---

## 📁 Project structure

```
fastapi-start-project/
│
├── app/
│   ├── main.py                     # Application entry point
│   │
│   ├── core/                       # Cross-cutting infrastructure
│   │   ├── config.py               # Typed settings (.env)
│   │   ├── database.py             # Engine, SessionLocal, Base
│   │   ├── security.py             # bcrypt + JWT
│   │   ├── logging.py              # Structured logger
│   │   ├── exceptions.py           # Global exception handlers
│   │   └── dependencies/
│   │       └── database.py         # get_db dependency
│   │
│   ├── auth/                       # Authentication
│   │   ├── models.py               # UserSession, RefreshToken, PasswordResetToken
│   │   ├── schemas.py
│   │   ├── service.py              # login, refresh, logout, password reset
│   │   ├── router.py
│   │   ├── deps.py                 # CurrentUser, CurrentAdmin, CurrentSessionId
│   │   └── exceptions.py
│   │
│   ├── users/                      # Identity & user management
│   │   ├── models.py               # UserModel, UserRole
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── router.py               # register, /users/me
│   │   ├── admin_router.py         # /admin/users
│   │   └── exceptions.py
│   │
│   └── audit/                      # Audit logs
│       ├── models.py
│       ├── service.py
│       └── constants.py
│
├── tests/                          # Pytest suite
│   ├── conftest.py                 # Shared fixtures
│   ├── auth/
│   └── users/
│
├── alembic/                        # Database migrations
├── scripts/
│   └── seed_admin.py               # Creates the first admin
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

- **Python 3.13** (avoid the bleeding-edge version if some C/Rust wheels aren't published yet)
- **pip** and **venv**
- _(optional)_ **Docker Desktop** if you want to run in containers

### Installation

```bash
# 1. Get the project (see "Using as a template" below) and enter the folder
cd my-project

# 2. Create and activate a virtual environment
python -m venv .venv

#    Linux / macOS
source .venv/bin/activate
#    Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env      # Windows: Copy-Item .env.example .env

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

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc
- **Health check** → http://localhost:8000/health

---

## ⚙️ Environment variables

All configuration lives in `.env` (never committed). Start from `.env.example`:

| Variable                      | Description                                   | Default                     |
|-------------------------------|-----------------------------------------------|-----------------------------|
| `APP_NAME`                    | Application name shown in docs                | `FastAPI Start Project`     |
| `APP_DESCRIPTION`             | Short description shown in docs               | _(generic)_                 |
| `APP_VERSION`                 | API version                                   | `1.0.0`                     |
| `APP_ENV`                     | Environment (`development` / `production`)    | `development`               |
| `DATABASE_URL`                | SQLAlchemy connection string                  | `sqlite:///./app.db`        |
| `SECRET_KEY`                  | JWT signing key — **required**, keep secret   | _(none — must be set)_      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes              | `60`                        |
| `ALGORITHM`                   | JWT signing algorithm                         | `HS256`                     |

> 🔒 **Never commit your `.env`.** It contains the `SECRET_KEY`. If it leaks,
> anyone can forge tokens for any user.

### Switching to PostgreSQL

Just change the connection string:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mydb
```

Then run `alembic upgrade head` again.

---

## 🐳 Running with Docker

```bash
# Build the image
docker compose build

# Start the container
docker compose up
```

The API will be available at http://localhost:8000/docs.

> The container name is derived from your project folder, so cloning this
> starter into a different folder renames it automatically — no edits needed.

---

## 🗄️ Database & migrations

This project uses **Alembic**. You never edit the schema by hand.

```bash
# Create a new migration after changing your models
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

> 💡 **Tip:** if `--autogenerate` produces an empty migration, make sure the
> target database does not already contain the tables and that your models are
> imported in `alembic/env.py`.

---

## 🌱 Creating the first admin

Public registration always creates `MEMBER` users. The very first `ADMIN` is
created via a seed script (solves the classic *bootstrap problem*):

```bash
python -m scripts.seed_admin
```

You'll be prompted for name, email and password. After that, admins are managed
through the protected `/admin/users` endpoints.

---

## 📚 API reference

All routes are prefixed with **`/api/v1`**.

### 🔓 Authentication

| Method | Endpoint                    | Auth | Description                              |
|--------|-----------------------------|------|------------------------------------------|
| `POST` | `/auth/register`            | ❌   | Register a new user (role = MEMBER)      |
| `POST` | `/auth/login`               | ❌   | Authenticate → access + refresh tokens   |
| `POST` | `/auth/refresh`             | ❌   | Rotate refresh token → new token pair    |
| `POST` | `/auth/logout`              | ✅   | Terminate the current session            |
| `POST` | `/auth/forgot-password`     | ❌   | Request a password reset token           |
| `POST` | `/auth/reset-password`      | ❌   | Reset the password using a token         |

### 👤 Users (self)

| Method  | Endpoint                | Auth | Description                          |
|---------|-------------------------|------|--------------------------------------|
| `GET`   | `/users/me`             | ✅   | Get the authenticated user's profile |
| `PATCH` | `/users/me`             | ✅   | Update profile (name, phone, bio…)   |
| `PATCH` | `/users/me/password`    | ✅   | Change own password                  |
| `DELETE`| `/users/me`             | ✅   | Deactivate own account (soft delete) |

### 🛡️ Admin

| Method  | Endpoint                        | Auth   | Description                       |
|---------|---------------------------------|--------|-----------------------------------|
| `POST`  | `/admin/users/`                 | 👑 ADMIN | Create a user with any role     |
| `GET`   | `/admin/users/`                 | 👑 ADMIN | List users (paginated, filters) |
| `PATCH` | `/admin/users/{user_id}`        | 👑 ADMIN | Update a user                   |
| `DELETE`| `/admin/users/{user_id}`        | 👑 ADMIN | Soft delete a user              |
| `DELETE`| `/admin/users/{user_id}/hard`   | 👑 ADMIN | Permanently delete a user       |

### ❤️ Health

| Method | Endpoint   | Auth | Description        |
|--------|------------|------|--------------------|
| `GET`  | `/health`  | ❌   | Service status     |

---

## 🔑 Authentication flow

```
┌────────────┐   POST /auth/login    ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │
│            │ ◀──────────────────── │            │
└────────────┘  access + refresh     └────────────┘
      │
      │  Authorization: Bearer <access_token>
      ▼
┌────────────┐   protected requests  ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │
└────────────┘                       └────────────┘
      │
      │  access token expired?
      ▼
┌────────────┐  POST /auth/refresh   ┌────────────┐
│   Client   │ ────────────────────▶ │    API     │  old refresh revoked,
│            │ ◀──────────────────── │            │  new pair issued
└────────────┘  new access+refresh   └────────────┘
```

- **Access token** — short-lived, sent on every request as a Bearer token.
- **Refresh token** — long-lived, used only to obtain new access tokens.
- **Rotation** — each refresh revokes the previous refresh token; reusing an old
  one is rejected (mitigates token theft).
- **Logout** — terminates the session, so even a non-expired access token stops
  working.

> ℹ️ The Swagger UI keeps the token only in memory, so refreshing the page logs
> you out there. In a real frontend (React, etc.), the token is stored client-side.

---

## 🧪 Running the tests

```bash
# Install test dependencies (if not already installed)
pip install pytest httpx

# Run the whole suite
pytest

# With coverage
pip install pytest-cov
pytest --cov=app
```

Tests use a **dedicated SQLite database** and recreate all tables before each
test, guaranteeing full isolation. The production/dev database is never touched.

Covered flows include:

- ✅ Register (success, duplicate email, weak password, full profile)
- ✅ Login (success, wrong password, unknown email)
- ✅ Refresh (success, invalid token, rotation revokes old token)
- ✅ Logout (success, access denied afterwards)
- ✅ Forgot / reset password (success, single-use token, invalid token)
- ✅ Profile (read, update, unauthorized)
- ✅ Password change (success, reuse blocked, wrong current)
- ✅ Self delete
- ✅ Admin (create, list, update, soft/hard delete, RBAC, self-delete guardrails)

---

## 🧩 Using as a template

This repository is designed to be reused. The recommended workflow:

### Option A — GitHub Template (recommended)

1. Push this project to GitHub.
2. Go to **Settings → General → check "Template repository"**.
3. For each new project, click **"Use this template"** — you get a fresh repo
   with no inherited commit history.

### Option B — Clone

```bash
git clone <your-repo-url> my-new-project
cd my-new-project
rm -rf .git && git init          # start a clean history
cp .env.example .env             # then personalize APP_NAME, DATABASE_URL, SECRET_KEY
```

### After creating your project

1. Edit `.env` → set your `APP_NAME`, `DATABASE_URL`, `SECRET_KEY`.
2. `alembic upgrade head`
3. `python -m scripts.seed_admin`
4. Start adding your **domain modules** under `app/` (e.g. `members/`,
   `products/`, `orders/`), following the same pattern:
   `models → schemas → service → router → exceptions`.

The starter foundation stays untouched — you only add on top of it.

---

## 🗺️ Roadmap

Ideas for future iterations of the starter:

- [ ] PostgreSQL as the default via Docker Compose
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Email delivery integration (SMTP / provider) for password reset
- [ ] Rate limiting on auth endpoints
- [ ] "Active sessions" management endpoint
- [ ] Granular permissions (beyond roles)

---

## 📄 License

Released under the **MIT License**. Feel free to use it in personal and
commercial projects.

---

<div align="center">

**Built with ❤️ and FastAPI.**

_If this starter saved you time, consider giving it a ⭐ on GitHub._

</div>
