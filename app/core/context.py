from fastapi import Depends
from pydantic import BaseModel
from app.core.auth import UserClaims, validate_token

class Context(BaseModel):
    user_id: str

def get_context(user: UserClaims = Depends(validate_token)) -> Context:
    return Context(user_id=user.sub)