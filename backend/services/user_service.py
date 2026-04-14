from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from models.user import User, UserResponse
import repositories.user_repository as repo

_ph = PasswordHasher()


def get_user_by_username(username: str) -> Optional[User]:
    return repo.get_user_by_username(username)


def get_user_by_id(user_id: str) -> Optional[User]:
    return repo.get_user_by_id(user_id)


def hash_password(plaintext: str) -> str:
    return _ph.hash(plaintext)


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_username(username)
    if not user:
        return None
    stored = user.password
    # Argon2 hashes start with $argon2; fall back to plaintext comparison for
    # unmigrated accounts so existing users are not locked out before migration.
    if stored.startswith("$argon2"):
        try:
            _ph.verify(stored, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return None
    else:
        if stored != password:
            return None
    return user


def update_user(user: User) -> User:
    return repo.save_user(user)


def to_user_response(user: User) -> UserResponse:
    return UserResponse(**user.model_dump(exclude={"password"}))
