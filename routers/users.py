from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from schemas.auth import UserOut
from schemas.post import PostOut
from models.user import User
from models.follow import Follow
from models.post import Post
from models.notification import Notification
from services.post_service import get_liked_post_ids
from utils.auth import get_current_user, bearer_scheme

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=UserOut)
async def get_profile(
    username: str,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    await get_current_user(credentials, db)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


@router.get("/{username}/posts", response_model=list[PostOut])
async def get_user_posts(
    username: str,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user(credentials, db)
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts_result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
    )
    posts = posts_result.scalars().all()
    liked_ids = await get_liked_post_ids([p.id for p in posts], current_user.id, db)
    result = []
    for p in posts:
        out = PostOut.model_validate(p)
        out.liked_by_me = p.id in liked_ids
        result.append(out)
    return result


@router.post("/{username}/follow")
async def follow_toggle(
    username: str,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user(credentials, db)
    target_result = await db.execute(select(User).where(User.username == username))
    target = target_result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    follow_result = await db.execute(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.following_id == target.id)
    )
    existing = follow_result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        current_user.following_count = max(0, current_user.following_count - 1)
        target.follower_count = max(0, target.follower_count - 1)
        await db.commit()
        return {"following": False}
    else:
        follow = Follow(follower_id=current_user.id, following_id=target.id)
        db.add(follow)
        current_user.following_count += 1
        target.follower_count += 1
        notif = Notification(user_id=target.id, actor_id=current_user.id, type="follow")
        db.add(notif)
        await db.commit()
        return {"following": True}


@router.get("", response_model=list[UserOut])
async def list_users(
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    await get_current_user(credentials, db)
    result = await db.execute(select(User).order_by(User.follower_count.desc()).limit(20))
    return [UserOut.model_validate(u) for u in result.scalars().all()]
