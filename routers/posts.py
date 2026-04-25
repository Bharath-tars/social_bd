from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.post import PostCreate, PostOut
from schemas.auth import UserOut
from services.post_service import create_post, get_post, delete_post, toggle_like, get_liked_post_ids
from utils.auth import get_current_user, bearer_scheme
from models.user import User

router = APIRouter(prefix="/posts", tags=["posts"])


def _enrich(post, liked_ids: set) -> PostOut:
    out = PostOut.model_validate(post)
    out.liked_by_me = post.id in liked_ids
    return out


@router.post("", response_model=PostOut, status_code=201)
async def create(
    data: PostCreate,
    background_tasks: BackgroundTasks,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    post = await create_post(data, user.id, db)
    # fire agent engagement asynchronously
    from agents.orchestrator import engage
    background_tasks.add_task(engage, post.id, post.content)
    liked_ids = await get_liked_post_ids([post.id], user.id, db)
    return _enrich(post, liked_ids)


@router.get("/{post_id}", response_model=PostOut)
async def get_one(
    post_id: int,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    post = await get_post(post_id, db)
    liked_ids = await get_liked_post_ids([post.id], user.id, db)
    return _enrich(post, liked_ids)


@router.delete("/{post_id}", status_code=204)
async def delete(
    post_id: int,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    await delete_post(post_id, user.id, db)


@router.post("/{post_id}/like")
async def like(
    post_id: int,
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    return await toggle_like(post_id, user.id, db)
