from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from models.post import Post
from models.follow import Follow


async def get_explore_feed(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Post]:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_home_feed(user_id: int, db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Post]:
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = list(following_result.scalars().all())
    following_ids.append(user_id)

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.user_id.in_(following_ids))
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_trending_feed(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Post]:
    since = datetime.now(timezone.utc) - timedelta(hours=48)
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.created_at >= since)
        .order_by(desc(Post.likes_count), desc(Post.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
