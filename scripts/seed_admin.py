"""Seed script: create the first ADMIN user.

Usage:
    python -m scripts.seed_admin

If an ADMIN user already exists, no action will be performed.
"""
import getpass
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.rbac.seed import seed_rbac, get_role_by_name
from app.users.exceptions import EmailAlreadyExistsError, WeakPasswordError
from app.users.models import UserModel
from app.users.service import create_user


def main() -> None:
    """Application entrypoint."""
    with SessionLocal() as db:
        # garante roles/permissions built-in (idempotente)
        seed_rbac(db)

        admin_role = get_role_by_name(db, "admin")
        if admin_role is None:
            print("Error: built-in 'admin' role not found after seeding.")
            sys.exit(1)

        # já existe algum admin? (checa por role_id agora)
        admin_exists = db.execute(
            select(UserModel).where(UserModel.role_id == admin_role.id)
        ).first()

        if admin_exists:
            print("An ADMIN user already exists. No action was performed.")
            sys.exit(0)

        print("=" * 60)
        print("🌱 Initial Seed — Create First ADMIN User")
        print("=" * 60)

        name = input("Enter the ADMIN user's name: ").strip()
        email = input("Enter the ADMIN user's email: ").strip()
        password = getpass.getpass("Enter the ADMIN user's password: ")

        try:
            create_user(
                db=db,
                name=name,
                email=email.lower(),
                password=password,
                role_name="admin",
            )
            print(f"ADMIN user '{name}' was created successfully.")
        except EmailAlreadyExistsError as exc:
            print(f"Error: {exc}")
        except WeakPasswordError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
