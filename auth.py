import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from database import (create_user, get_user_by_username, get_user_by_id, save_remember_token, get_user_by_remember_token, revoke_remember_token)

ITERATIONS = 310_000

def hash_password(password, salt):
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS)
    return derived.hex()

def register_user(username,password, confirm_password):
    username = username.strip().lower()

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if password != confirm_password:
        return False, "Passwords do not match."
    if get_user_by_username(username):
        return False, "username is already registered."

    salt = secrets.token_bytes(16).hex()
    password_hash = hash_password(password, salt)

    try:
        create_user(username, password_hash, salt)
    except Exception:
        return False, "Unable to create the account, please try again later."
    return True, "Account created successfully. You can now log in."

def authenticate_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return None

    candidate_hash = hash_password(password, user["password_salt"])
    if candidate_hash != user["password_hash"]:
        return None
    return {
        "user_id": user["user_id"],
        "username": user["username"]
    }

def create_remember_token(user_id, days=30):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    save_remember_token(user_id, token_hash, expires_at)
    return token

def authenticate_remember_token(token):
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return get_user_by_remember_token(token_hash)

def revoke_token(token):
    if token:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        revoke_remember_token(token_hash)

def get_public_user(user_id):
    return get_user_by_id(user_id)