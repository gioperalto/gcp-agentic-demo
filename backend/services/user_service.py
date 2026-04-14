from typing import Optional
from models.user import User, UserResponse
import repositories.user_repository as repo


def get_user_by_username(username: str) -> Optional[User]:
    return repo.get_user_by_username(username)


def get_user_by_id(user_id: str) -> Optional[User]:
    return repo.get_user_by_id(user_id)


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_username(username)
    if user and user.password == password:
        return user
    return None


def update_user(user: User) -> User:
    return repo.save_user(user)


def to_user_response(user: User) -> UserResponse:
    return UserResponse(**user.model_dump(exclude={"password"}))
