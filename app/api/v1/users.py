from fastapi import APIRouter, Depends, HTTPException

from app.core.context import Context, get_context
from app.core.exceptions import (
    AlreadyExistsError,
    AuthClientError,
    DatabaseError,
    NotFoundError,
    PermissionDeniedError,
    S3UploadError,
)
from app.model.user_model import (
    CreateUserReq,
    CreateUserResp,
    GetLocationUsersResp,
    UpdateUserReq,
    UpdateUserResp,
    UploadProfilePictureReq,
    UploadProfilePictureResp,
)
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
    except AuthClientError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    except AlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return user


@router.patch("/users/{user_id}", response_model=UpdateUserResp)
def update_user(
    req: UpdateUserReq,
    user_id: str,
    ctx: Context = Depends(get_context),
    user_service: UserService = Depends(),
) -> UpdateUserResp:
    try:
        user_service.update_user(
            context=ctx,
            user_id=user_id,
            email=req.email,
            first_name=req.first_name,
            last_name=req.last_name,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except AuthClientError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    return UpdateUserResp()


@router.post(
    "/users/{user_id}/profile-picture", response_model=UploadProfilePictureResp
)
def upload_profile_picture(
    req: UploadProfilePictureReq,
    user_id: str,
    ctx: Context = Depends(get_context),
    user_service: UserService = Depends(),
) -> UploadProfilePictureResp:
    try:
        resp = user_service.upload_profile_picture(
            context=ctx,
            user_id=user_id,
            base64=req.base64,
            extension=req.extension,
        )
    except AlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    except AuthClientError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    except S3UploadError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return resp


@router.get("/locations/{location_id}/users", response_model=GetLocationUsersResp)
def get_location_users(
    location_id: str,
    ctx: Context = Depends(get_context),
    user_service: UserService = Depends(),
) -> GetLocationUsersResp:
    try:
        users = user_service.get_location_users(
            context=ctx,
            location_id=location_id,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except AuthClientError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except PermissionDeniedError as err:
        raise HTTPException(status_code=403, detail=str(err)) from err
    return GetLocationUsersResp(location_id=location_id, users=users)
