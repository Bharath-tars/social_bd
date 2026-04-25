from datetime import datetime
from pydantic import BaseModel
from schemas.auth import UserOut


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    post_id: int
    user_id: int
    content: str
    is_ai_generated: bool
    created_at: datetime
    author: UserOut
