import asyncio
import random

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import AsyncSessionLocal
from models.comment import Comment
from models.notification import Notification
from models.user import User
from agents.commenter import generate_comment
from agents.personas import AGENT_PERSONAS


async def engage(post_id: int, post_content: str) -> None:
    await asyncio.sleep(random.uniform(3, 10))

    chosen = random.sample(AGENT_PERSONAS, k=random.randint(1, 2))

    async with AsyncSessionLocal() as db:
        for persona in chosen:
            agent_result = await db.execute(
                select(User).where(User.username == persona["name"], User.is_agent == True)
            )
            agent_user = agent_result.scalar_one_or_none()
            if not agent_user:
                continue

            comment_text = await generate_comment(persona, post_content)

            comment = Comment(
                post_id=post_id,
                user_id=agent_user.id,
                content=comment_text,
                is_ai_generated=True,
            )
            db.add(comment)

            from models.post import Post
            post_result = await db.execute(select(Post).where(Post.id == post_id))
            post = post_result.scalar_one_or_none()
            if post:
                post.comments_count += 1
                if post.user_id != agent_user.id:
                    notif = Notification(
                        user_id=post.user_id,
                        actor_id=agent_user.id,
                        type="ai_comment",
                        post_id=post_id,
                    )
                    db.add(notif)

        await db.commit()
