from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class Role(str, Enum):
    TEAM_MEMBER = "TEAM_MEMBER"
    TEAM_LEADER = "TEAM_LEADER"
    DIRECTOR = "DIRECTOR"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"


class Membership(BaseModel):
    user_id: str
    location_id: str
    roles: set[Role]
    created_at: str
    updated_at: str


class CreateMembershipReq(BaseModel):
    user_id: str
    roles: set[Role] = Field(min_length=1)


class UpdateMembershipReq(BaseModel):
    roles: set[Role] = Field(min_length=1)


class MembershipResp(Membership):
    pass


class UserMembership(BaseModel):
    location_id: str
    roles: set[Role]


class LocationMembership(BaseModel):
    user_id: str
    roles: set[Role]


class GetUserMembershipsResp(BaseModel):
    user_id: str
    memberships: List[UserMembership]


class GetLocationMembershipsResp(BaseModel):
    location_id: str
    memberships: List[LocationMembership]
