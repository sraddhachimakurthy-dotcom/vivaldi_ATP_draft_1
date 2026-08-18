"""
SAI PRAVESH — Admin credentials.

Credentials are loaded from environment variables (see .env.example) instead
of being hardcoded in source, so this file is safe to commit.
Set ADMIN_1, ADMIN_2, ADMIN_3, ... in your .env as:
    username:password:role:Display Name
"""

import os

VALID_ROLES = {"superadmin", "director", "staff"}


def _load_admins():
    admins = []
    i = 1
    while True:
        raw = os.getenv(f"ADMIN_{i}")
        if not raw:
            break
        parts = raw.split(":", 3)
        if len(parts) != 4:
            i += 1
            continue
        username, password, role, name = parts
        if role not in VALID_ROLES:
            i += 1
            continue
        admins.append({
            "username": username,
            "password": password,
            "role": role,
            "name": name,
        })
        i += 1
    return admins


ADMINS = _load_admins()