from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.notification import NotificationOut
from services.notification_service import get_notifications, mark_all_read, unread_count
from utils.auth import get_current_user, bearer_scheme

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    notifications = await get_notifications(user.id, db)
    return [NotificationOut.model_validate(n) for n in notifications]


@router.get("/unread-count")
async def get_unread_count(
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    count = await unread_count(user.id, db)
    return {"count": count}


@router.patch("/read", status_code=204)
async def mark_read(
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    await mark_all_read(user.id, db)
