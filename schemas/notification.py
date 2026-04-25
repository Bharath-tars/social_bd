from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.auth import UserOut


class NotificationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    type: str
    post_id: Optional[int]
    read: bool
    created_at: datetime
    actor: UserOut
