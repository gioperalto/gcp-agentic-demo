import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path
from models.user import User, UserResponse

DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"

def _load_users() -> List[User]:
    """Load users from JSON file"""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return [User(**user) for user in data]

def _save_users(users: List[User]):
    """Save users to JSON file"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump([user.model_dump() for user in users], f, indent=2)

def get_user_by_username(username: str) -> Optional[User]:
    """Find user by username"""
    users = _load_users()
    return next((u for u in users if u.username == username), None)

def get_user_by_id(user_id: str) -> Optional[User]:
    """Find user by ID"""
    users = _load_users()
    return next((u for u in users if u.id == user_id), None)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if user and user.password == password:
        return user
    return None

def update_user(user: User) -> User:
    """Update user data"""
    users = _load_users()
    user.updatedAt = datetime.utcnow().isoformat()
    users = [u if u.id != user.id else user for u in users]
    _save_users(users)
    return user

def to_user_response(user: User) -> UserResponse:
    """Convert User to UserResponse (removing password)"""
    return UserResponse(**user.model_dump(exclude={'password'}))
