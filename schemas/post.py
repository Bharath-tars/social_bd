from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.auth import UserOut


class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None


class PostOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    content: str
    image_url: Optional[str]
    likes_count: int
    comments_count: int
    created_at: datetime
    author: UserOut
    liked_by_me: bool = False
