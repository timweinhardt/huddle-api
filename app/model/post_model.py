from typing import List, Optional
from pydantic import BaseModel

class Post(BaseModel):
    id: str
    author_id: str
    location_id: str
    title: str
    content: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

class CreatePostReq(BaseModel):
    location_id: str
    title: str
    content: str

class CreatePostResp(Post):
    pass

class GetPostByIdResp(Post):
    pass

class GetPostsByLocationIdResp(BaseModel):
    posts: List[Post]

class UpdatePostReq(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class UpdatePostResp(Post):
    pass

class DeletePostResp(Post):
    pass