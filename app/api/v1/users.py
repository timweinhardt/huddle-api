from fastapi import APIRouter, Depends, HTTPException

from app.core.context import Context, get_context
from app.core.exceptions import AlreadyExistsError, DatabaseError, PermissionDeniedError
from app.model.user_model import CreateUserReq, CreateUserResp
from app.service.user_service import UserService

router = APIRouter()


@router.post("/users", response_model=CreateUserResp)
def create_user(
    req: CreateUserReq,
    ctx: Context = Depends(get_context),
    user_service: UserService = Depends(),
) -> CreateUserResp:
    try:
        user = user_service.create_user(
            context=ctx,
            email=req.email,
            first_name=req.first_name,
            last_name=req.last_name,
            memberships=req.memberships,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    except AlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return user
