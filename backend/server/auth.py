"""
server/auth.py — Authentication and session management for ArecaVision AI.
Uses Python standard library (hashlib, hmac, secrets) for zero-dependency portability.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from server.db import _DB_LOCK, _get_conn

_logger = logging.getLogger("arecavision.auth")
JWT_SECRET = os.getenv("JWT_SECRET", "ARECAVISION_AI_ENTERPRISE_SECRET_KEY_2026_PRODUCTION")


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2_sha256${salt}${dk.hex()}"


def _verify_password(password: str, hashed: str) -> bool:
    try:
        parts = hashed.split("$")
        if len(parts) == 3 and parts[0] == "pbkdf2_sha256":
            salt = parts[1]
            target_hex = parts[2]
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
            return hmac.compare_digest(dk.hex(), target_hex)
        # Fallback for plain demo passwords or legacy strings
        return password == hashed
    except Exception:
        return False


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def create_jwt(user_id: str, role: str = "farmer", expires_in: int = 86400) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": now + expires_in,
    }
    h_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    p_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    seg1 = _b64_encode(h_bytes)
    seg2 = _b64_encode(p_bytes)
    signing_input = f"{seg1}.{seg2}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{seg1}.{seg2}.{_b64_encode(sig)}"


def verify_jwt(token: str) -> Optional[dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_decode(parts[2])
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_b64_decode(parts[1]).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def init_auth_tables() -> None:
    with _DB_LOCK:
        conn = _get_conn()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'farmer',
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    must_change_password INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            # Seed default demo accounts
            cur = conn.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0:
                now_str = datetime.now(timezone.utc).isoformat()
                defaults = [
                    ("admin", "admin@arecavision.ai", "admin123", "System Administrator", "admin"),
                    ("farmer", "farmer@arecavision.ai", "farmer123", "Ramesh Gowda", "farmer"),
                    ("agronomist", "agronomist@arecavision.ai", "agro123", "Dr. A. K. Hegde", "agronomist"),
                ]
                for u, e, p, n, r in defaults:
                    uid = f"usr-{u}-{secrets.token_hex(4)}"
                    pw_hash = _hash_password(p)
                    conn.execute(
                        """
                        INSERT INTO users (id, username, email, password_hash, name, role, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (uid, u, e, pw_hash, n, r, now_str),
                    )
            conn.commit()
        finally:
            conn.close()


def register_user(username: str, email: str, password: str, name: str) -> dict[str, Any]:
    username = username.strip().lower()
    email = email.strip().lower()
    name = name.strip()
    if not username or len(username) < 3 or len(username) > 32:
        raise ValueError("Username must be between 3 and 32 characters.")
    if not all(ch.isalnum() or ch in "._-" for ch in username):
        raise ValueError("Username can contain letters, numbers, dots, underscores, and hyphens.")
    if not email or "@" not in email or len(email) > 254:
        raise ValueError("Enter a valid email address.")
    if not name or len(name) > 80:
        raise ValueError("Name must be between 1 and 80 characters.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    with _DB_LOCK:
        conn = _get_conn()
        try:
            cur = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cur.fetchone():
                raise ValueError("A user with this username or email already exists.")
            uid = f"usr-{uuid.uuid4().hex[:10]}"
            now_str = datetime.now(timezone.utc).isoformat()
            pw_hash = _hash_password(password)
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, name, role, created_at)
                VALUES (?, ?, ?, ?, ?, 'farmer', ?)
                """,
                (uid, username, email, pw_hash, name, now_str),
            )
            conn.commit()
            return {
                "id": uid,
                "username": username,
                "email": email,
                "name": name,
                "role": "farmer",
            }
        finally:
            conn.close()


def authenticate_user(identifier: str, password: str) -> Optional[dict[str, Any]]:
    identifier = identifier.strip().lower()
    with _DB_LOCK:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "SELECT id, username, email, password_hash, name, role FROM users WHERE username = ? OR email = ?",
                (identifier, identifier),
            )
            row = cur.fetchone()
            if not row:
                return None

            if not _verify_password(password, row["password_hash"]):
                return None

            user = {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"],
            }
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), row["id"]),
            )
            conn.commit()
            token = create_jwt(user["id"], user["role"])
            return {"user": user, "token": token}
        finally:
            conn.close()


def update_user_profile(user_id: str, username: str, email: str, name: str) -> dict[str, Any]:
    username = username.strip().lower()
    email = email.strip().lower()
    name = name.strip()
    if not username or len(username) < 3 or len(username) > 32:
        raise ValueError("Username must be between 3 and 32 characters.")
    if not all(ch.isalnum() or ch in "._-" for ch in username):
        raise ValueError("Username can contain letters, numbers, dots, underscores, and hyphens.")
    if not email or "@" not in email or len(email) > 254:
        raise ValueError("Enter a valid email address.")
    if not name or len(name) > 80:
        raise ValueError("Name must be between 1 and 80 characters.")
    with _DB_LOCK:
        conn = _get_conn()
        try:
            duplicate = conn.execute(
                "SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?",
                (username, email, user_id),
            ).fetchone()
            if duplicate:
                raise ValueError("That username or email is already in use.")
            cur = conn.execute(
                "UPDATE users SET username = ?, email = ?, name = ? WHERE id = ?",
                (username, email, name, user_id),
            )
            if cur.rowcount == 0:
                raise ValueError("User not found.")
            conn.commit()
            updated = conn.execute(
                "SELECT id, username, email, name, role FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            return {
                "id": updated["id"],
                "username": updated["username"],
                "email": updated["email"],
                "name": updated["name"],
                "role": updated["role"],
            }
        finally:
            conn.close()


def get_user_by_id(user_id: str) -> Optional[dict[str, Any]]:
    with _DB_LOCK:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "SELECT id, username, email, name, role FROM users WHERE id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"],
            }
        finally:
            conn.close()


def get_all_users() -> list[dict[str, Any]]:
    with _DB_LOCK:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "SELECT id, username, email, name, role, created_at, last_login FROM users ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r["id"],
                    "username": r["username"],
                    "email": r["email"],
                    "name": r["name"],
                    "role": r["role"],
                    "createdAt": r["created_at"],
                    "lastLogin": r["last_login"],
                    "scanCount": 14,
                }
                for r in rows
            ]
        finally:
            conn.close()


def change_user_password(user_id: str, old_pw: str, new_pw: str) -> bool:
    with _DB_LOCK:
        conn = _get_conn()
        try:
            cur = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if not row or not _verify_password(old_pw, row["password_hash"]):
                return False
            new_hash = _hash_password(new_pw)
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            return True
        finally:
            conn.close()
