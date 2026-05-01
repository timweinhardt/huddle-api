from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.context import Context, get_context
from app.core.exceptions import AlreadyExistsError, DatabaseError, NotFoundError
from app.model.membership_model import CreateMembershipReq, GetLocationMembershipsResp, GetUserMembershipsResp, MembershipResp, UpdateMembershipReq
from app.service.membership_service import MembershipService

router = APIRouter()

@router.post("/locations/{location_id}/memberships", response_model=MembershipResp)
def create_membership(
    req: CreateMembershipReq,
    location_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> MembershipResp:
    try:
        new_membership = membership_service.create_membership(
            user_id=req.user_id,
            location_id=location_id,
            roles=req.roles
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except AlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err))
    return new_membership

@router.get("/locations/{location_id}/memberships/{user_id}", response_model=MembershipResp)
def get_membership(
    location_id: str,
    user_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> MembershipResp:
    try:
        membership = membership_service.get_membership(
            user_id=user_id,
            location_id=location_id,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return membership

@router.put("/locations/{location_id}/memberships/{user_id}", response_model=MembershipResp)
def update_membership(
    req: UpdateMembershipReq,
    location_id: str,
    user_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> MembershipResp:
    try:
        updated_membership = membership_service.update_membership_roles(
            user_id=user_id,
            location_id=location_id,
            roles=req.roles
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return updated_membership

@router.delete("/locations/{location_id}/memberships/{user_id}")
def delete_membership(
    location_id: str,
    user_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> Response:
    try:
        membership_service.delete_membership(
            user_id=user_id,
            location_id=location_id,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return Response(content=None)

@router.get("/users/{user_id}/memberships", response_model=GetUserMembershipsResp)
def get_user_memberships(
    user_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> GetUserMembershipsResp:
    try:
        user_memberships = membership_service.get_user_memberships(
            user_id=user_id,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return GetUserMembershipsResp(user_id=user_id, memberships=user_memberships)

@router.get("/locations/{location_id}/memberships", response_model=GetLocationMembershipsResp)
def get_location_memberships(
    location_id: str,
    ctx: Context = Depends(get_context),
    membership_service: MembershipService = Depends()
) -> GetLocationMembershipsResp:
    try:
        location_memberships = membership_service.get_location_memberships(
            location_id=location_id,
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return GetLocationMembershipsResp(location_id=location_id, memberships=location_memberships)