from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import UserClaims, validate_token
from app.core.exceptions import DatabaseError, NotFoundError
from app.model.post_model import CreatePostReq, CreatePostResp, DeletePostResp, GetPostsByLocationIdReq, GetPostsByLocationIdResp, GetPostByIdResp, UpdatePostReq, UpdatePostResp
from app.service.post_service import PostService

router = APIRouter()

@router.post("/posts", response_model=CreatePostResp)
def create_post(
    req: CreatePostReq,
    user: UserClaims = Depends(validate_token),
    post_service: PostService = Depends()
) -> CreatePostResp:
    try:
        new_post = post_service.create_post(
            author_id=user.sub,
            location_id=req.location_id,
            title=req.title,
            content=req.content
        )
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    return new_post

@router.get("/posts/{id}", response_model=GetPostByIdResp)
def get_post_by_id(
    id: str,
    include_deleted: bool = False,
    user: UserClaims = Depends(validate_token),
    post_service: PostService = Depends()
) -> GetPostByIdResp:
    try:
        post = post_service.get_post_by_id(id, include_deleted=include_deleted)
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return post

@router.get("/posts", response_model=GetPostsByLocationIdResp)
def get_posts_by_location_id(
    req: GetPostsByLocationIdReq,
    include_deleted: bool = False,
    user: UserClaims = Depends(validate_token),
    post_service: PostService = Depends()
) -> GetPostsByLocationIdResp:
    try:
        posts = post_service.get_posts_by_location_id(req.location_id, include_deleted=include_deleted)
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    return GetPostsByLocationIdResp(posts=posts)

@router.patch("/posts/{id}", response_model=UpdatePostResp)
def update_post(
    req: UpdatePostReq,
    id: str,
    user: UserClaims = Depends(validate_token),
    post_service: PostService = Depends()
) -> UpdatePostResp:
    try:
        updated_post = post_service.update_post(id, title=req.title, content=req.content)
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return updated_post

@router.delete("/posts/{id}", response_model=DeletePostResp)
def delete_post(
    id: str,
    user: UserClaims = Depends(validate_token),
    post_service: PostService = Depends()
) -> DeletePostResp:
    try:
        deleted_post = post_service.delete_post(id)
    except DatabaseError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    return deleted_post