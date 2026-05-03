from typing import List, Optional
from pydantic import BaseModel

from app.model.membership_model import UserMembership

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    memberships: List[UserMembership]
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

class CreateUserReq(BaseModel):
    email: str
    first_name: str
    last_name: str
    memberships: List[UserMembership]

class CreateUserResp(User):
    pass