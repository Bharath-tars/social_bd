from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from models.post import Post
from models.like import Like
from models.notification import Notification
from schemas.post import PostCreate


async def create_post(data: PostCreate, user_id: int, db: AsyncSession) -> Post:
    post = Post(user_id=user_id, content=data.content, image_url=data.image_url)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.id == post.id)
    )
    return result.scalar_one()


async def get_post(post_id: int, db: AsyncSession) -> Post:
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def delete_post(post_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
    await db.delete(post)
    await db.commit()


async def toggle_like(post_id: int, user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing_like = like_result.scalar_one_or_none()

    if existing_like:
        await db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        await db.commit()
        return {"liked": False, "likes_count": post.likes_count}
    else:
        like = Like(post_id=post_id, user_id=user_id)
        db.add(like)
        post.likes_count += 1
        if post.user_id != user_id:
            notif = Notification(user_id=post.user_id, actor_id=user_id, type="like", post_id=post_id)
            db.add(notif)
        await db.commit()
        return {"liked": True, "likes_count": post.likes_count}


async def get_liked_post_ids(post_ids: list[int], user_id: int, db: AsyncSession) -> set[int]:
    if not post_ids:
        return set()
    result = await db.execute(
        select(Like.post_id).where(Like.post_id.in_(post_ids), Like.user_id == user_id)
    )
    return set(result.scalars().all())
