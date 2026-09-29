# @index-begin
# @symbol function/class: main L30
# @symbol variable/parameter: parser L32
# @symbol variable/parameter: subparsers L36
# @symbol variable/parameter: workspace L37
# @symbol variable/parameter: user L40
# @symbol variable/parameter: backup L45
# @symbol variable/parameter: args L47
# @symbol variable/parameter: path L48
# @symbol variable/parameter: config L51
# @symbol variable/parameter: database L52
# @symbol variable/parameter: row L59
# @symbol variable/parameter: password L67
# @symbol variable/parameter: destination L82
# @symbol variable/parameter: target L88
# @index-end
"""Operator CLI for clean workspaces, user provisioning and consistent backups. Index: docs/code-index.md."""

import argparse
import getpass
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from .models import WorkspaceConfig
from .store import connect, initialize, password_hash


def main():
    """Provision accounts interactively; never accept plaintext passwords in command arguments."""
    parser = argparse.ArgumentParser(
        description="Workbench administration (run only on a trusted host)"
    )
    parser.add_argument("--db", default=os.environ.get("KB_DB", "data/workbench.sqlite"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    workspace = subparsers.add_parser("workspace")
    workspace.add_argument("id")
    workspace.add_argument("title")
    user = subparsers.add_parser("user")
    user.add_argument("workspace")
    user.add_argument("username")
    user.add_argument("role", choices=["customer", "employee", "admin"])
    user.add_argument("--customer")
    backup = subparsers.add_parser("backup")
    backup.add_argument("destination")
    args = parser.parse_args()
    path = Path(args.db)
    initialize(path, False)
    if args.command == "workspace":
        config = WorkspaceConfig(title=args.title, profile=args.id)
        with connect(path) as database:
            database.execute(
                "INSERT INTO workspaces VALUES (?,?)", (args.id, config.model_dump_json())
            )
        print("Workspace created without sample data or demo accounts")
    elif args.command == "user":
        with connect(path) as database:
            row = database.execute(
                "SELECT config FROM workspaces WHERE id=?", (args.workspace,)
            ).fetchone()
            if not row:
                raise SystemExit("Create the workspace first")
            config = WorkspaceConfig.model_validate_json(row[0])
            if args.role == "customer" and args.customer not in config.customers:
                raise SystemExit("Customer must match a configured customer ID")
            password = getpass.getpass("New password (12+ characters): ")
            if len(password) < 12 or password != getpass.getpass("Confirm password: "):
                raise SystemExit("Password too short or confirmation differs")
            database.execute(
                "INSERT INTO users(workspace,username,password,role,customer) VALUES (?,?,?,?,?)",
                (
                    args.workspace,
                    args.username,
                    password_hash(password),
                    args.role,
                    args.customer if args.role == "customer" else None,
                ),
            )
        print("Account created")
    else:
        destination = Path(args.destination)
        if destination.exists() or destination.resolve() == path.resolve():
            raise SystemExit(
                "Backup destination must be a new file distinct from the live database"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        with connect(path) as database, closing(sqlite3.connect(destination)) as target:
            database.backup(target)
        print("Consistent SQLite backup created; protect it as sensitive data")


if __name__ == "__main__":
    main()
