from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from models.notification import Notification


async def get_notifications(user_id: int, db: AsyncSession, limit: int = 30) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .options(selectinload(Notification.actor), selectinload(Notification.post))
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def mark_all_read(user_id: int, db: AsyncSession) -> None:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read == False)
        .values(read=True)
    )
    await db.commit()


async def unread_count(user_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id, Notification.read == False)
    )
    return len(result.scalars().all())
