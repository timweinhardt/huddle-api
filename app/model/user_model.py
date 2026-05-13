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
    is_confirmed: bool


class CreateUserReq(BaseModel):
    email: str
    first_name: str
    last_name: str
    memberships: List[UserMembership]


class CreateUserResp(User):
    pass


class UploadProfilePictureReq(BaseModel):
    base64: Optional[str] = None
    extension: Optional[str] = None


class UpdateUserReq(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture_url: Optional[str] = None


class InviteUserReq(BaseModel):
    email: str
    first_name: str
    last_name: str
    memberships: List[UserMembership]


class InviteUserResp(BaseModel):
    pass


class UpdateUserResp(BaseModel):
    pass


class UploadProfilePictureResp(BaseModel):
    picture_url: str


class GetLocationUsersResp(BaseModel):
    location_id: str
    users: List[User]
