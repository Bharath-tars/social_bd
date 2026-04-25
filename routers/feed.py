from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.post import PostOut
from services.feed_service import get_explore_feed, get_home_feed, get_trending_feed
from services.post_service import get_liked_post_ids
from utils.auth import get_current_user, bearer_scheme

router = APIRouter(prefix="/feed", tags=["feed"])


def _enrich_list(posts, liked_ids):
    result = []
    for p in posts:
        out = PostOut.model_validate(p)
        out.liked_by_me = p.id in liked_ids
        result.append(out)
    return result


@router.get("/explore", response_model=list[PostOut])
async def explore(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    posts = await get_explore_feed(db, skip, limit)
    liked_ids = await get_liked_post_ids([p.id for p in posts], user.id, db)
    return _enrich_list(posts, liked_ids)


@router.get("/home", response_model=list[PostOut])
async def home(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    posts = await get_home_feed(user.id, db, skip, limit)
    liked_ids = await get_liked_post_ids([p.id for p in posts], user.id, db)
    return _enrich_list(posts, liked_ids)


@router.get("/trending", response_model=list[PostOut])
async def trending(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(credentials, db)
    posts = await get_trending_feed(db, skip, limit)
    liked_ids = await get_liked_post_ids([p.id for p in posts], user.id, db)
    return _enrich_list(posts, liked_ids)
