from fastapi import APIRouter

router = APIRouter()

@router.get("/posts")
def get_users():
    return {"message": "Hello, World!!!"}