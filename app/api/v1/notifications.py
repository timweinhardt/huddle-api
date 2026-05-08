from fastapi import APIRouter, Depends, HTTPException

from app.core.context import Context, get_context
from app.core.exceptions import (
    AlreadyExistsError,
    AuthClientError,
    DatabaseError,
    PermissionDeniedError,
)
from app.model.notification_model import RegisterPushTokenReq, RegisterPushTokenResp
from app.service.push_token_repository import ExponentPushTokenRepository

router = APIRouter()


@router.post("/register_push_token", response_model=RegisterPushTokenResp)
def register_push_token(
    req: RegisterPushTokenReq,
    ctx: Context = Depends(get_context),
    token_repo: ExponentPushTokenRepository = Depends(),
) -> RegisterPushTokenResp:
    try:
        token_repo.register_token(user_id=ctx.user_id, push_token=req.push_token)
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except AuthClientError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    except AlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return RegisterPushTokenResp()
