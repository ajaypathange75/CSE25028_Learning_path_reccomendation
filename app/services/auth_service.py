import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, UserSession

# Secure password hashing using PBKDF2-HMAC-SHA256 (standard library, highly secure, no external compilation required)
HASH_ALGORITHM = "sha256"
ITERATIONS = 350_000
SALT_BYTES = 16

def hash_password(password: str) -> str:
    """Hashes a password with a unique random salt using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2:{HASH_ALGORITHM}:{ITERATIONS}${salt.hex()}${dk.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash."""
    try:
        header, salt_hex, hash_hex = hashed_password.split("$")
        parts = header.split(":")
        algo = parts[1]
        iterations = int(parts[2])
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        
        computed_hash = hashlib.pbkdf2_hmac(algo, plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(computed_hash, expected_hash)
    except Exception:
        return False

def create_user(db: Session, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
    """Creates a new user record with securely hashed password."""
    # Check duplicate
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        if existing_user.username == username:
            raise ValueError("Username already taken")
        else:
            raise ValueError("Email already registered")
            
    hashed = hash_password(password)
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=hashed,
        full_name=full_name.strip() if full_name else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Authenticates a user by username or email."""
    query = username_or_email.strip()
    user = db.query(User).filter((User.username == query) | (User.email == query.lower())).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_session(db: Session, user_id: int) -> UserSession:
    """Creates a new secure session token."""
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)
    
    session_obj = UserSession(
        user_id=user_id,
        session_token=token,
        expires_at=expires_at
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj

def get_user_from_session(db: Session, session_token: Optional[str]) -> Optional[User]:
    """Validates session token and returns active user if valid and not expired."""
    if not session_token:
        return None
    
    session_obj = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session_obj:
        return None
    
    return session_obj.user

def revoke_session(db: Session, session_token: Optional[str]) -> bool:
    """Invalidates session on logout."""
    if not session_token:
        return False
    session_obj = db.query(UserSession).filter(UserSession.session_token == session_token).first()
    if session_obj:
        db.delete(session_obj)
        db.commit()
        return True
    return False
