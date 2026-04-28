from fastapi import APIRouter, Depends
from app.core.auth import UserClaims, validate_token

router = APIRouter()

@router.get("/posts")
def get_users(user: UserClaims = Depends(validate_token)):
    return {"message": f"Hello, {user.sub}!!!"}