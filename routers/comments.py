from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from schemas.comment import CommentCreate, CommentOut
from models.comment import Comment
from models.post import Post
from models.notification import Notification
from utils.auth import get_current_user, bearer_scheme

router = APIRouter(prefix="/posts", tags=["comments"])


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: int,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    await get_current_user(credentials, db)
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at)
    )
    return [CommentOut.model_validate(c) for c in result.scalars().all()]


@router.post("/{post_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    post_id: int,
    data: CommentCreate,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)

    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(post_id=post_id, user_id=user.id, content=data.content)
    db.add(comment)
    post.comments_count += 1

    if post.user_id != user.id:
        notif = Notification(user_id=post.user_id, actor_id=user.id, type="comment", post_id=post_id)
        db.add(notif)

    await db.commit()
    await db.refresh(comment)

    result = await db.execute(
        select(Comment).options(selectinload(Comment.author)).where(Comment.id == comment.id)
    )
    return CommentOut.model_validate(result.scalar_one())
