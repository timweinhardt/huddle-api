from pydantic import BaseModel


class UserPushToken(BaseModel):
    user_id: str
    push_token: str


class RegisterPushTokenReq(BaseModel):
    user_id: str
    push_token: str


class UnregisterPushTokenReq(BaseModel):
    push_token: str


class RegisterPushTokenResp(BaseModel):
    pass

class UnregisterPushTokenResp(BaseModel):
    pass
