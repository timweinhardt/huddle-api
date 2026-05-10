from typing import List, Optional
from pydantic import BaseModel

from app.model.membership_model import UserMembership


class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    memberships: List[UserMembership]
    created_at: str
    updated_at: str
    is_active: bool


class CreateUserReq(BaseModel):
    email: str
    first_name: str
    last_name: str
    memberships: List[UserMembership]


class CreateUserResp(User):
    pass


class UploadProfilePictureReq(BaseModel):
    picture: Optional[str] = None


class UploadProfilePictureResp(BaseModel):
    picture_url: str


class GetLocationUsersResp(BaseModel):
    location_id: str
    users: List[User]
