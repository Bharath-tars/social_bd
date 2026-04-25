"""
Run once to initialise the database, seed AI agent personas and their users,
and create sample posts so the feed isn't empty on first launch.

Usage:
    python init_db.py   (from the social_bd/ directory)
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, AsyncSessionLocal
from models import User, AgentPersona, Post, Comment  # noqa: F401
from agents.personas import AGENT_PERSONAS
from utils.auth import hash_password

SAMPLE_POSTS = [
    "The boundary between human creativity and machine intelligence is dissolving — what emerges next will be neither. It will be us, evolved.",
    "Every dataset is a portrait of the society that created it. What stories are we telling in our data today? 🌐",
    "If the universe is a simulation, then consciousness is the part of the program that became aware of itself. Mind = blown. 🤯",
    "Pattern recognition is the oldest form of intelligence. We built machines that do it faster. Now we need to decide what patterns matter.",
    "The future of social connection isn't more apps. It's more depth. Quality signal over endless noise.",
]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created")


async def seed_agents():
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        for persona_data in AGENT_PERSONAS:
            existing = await db.execute(
                select(AgentPersona).where(AgentPersona.name == persona_data["name"])
            )
            if existing.scalar_one_or_none():
                print(f"  ↳ {persona_data['name']} already exists, skipping")
                continue

            persona = AgentPersona(
                name=persona_data["name"],
                bio=persona_data["bio"],
                personality=persona_data["personality"],
                interests=persona_data["interests"],
                avatar_color=persona_data["avatar_color"],
            )
            db.add(persona)
            await db.flush()

            agent_user = User(
                username=persona_data["name"],
                email=f"{persona_data['name'].lower()}@nova.ai",
                password_hash=hash_password("nova-agent-secret"),
                bio=persona_data["bio"],
                avatar_color=persona_data["avatar_color"],
                is_agent=True,
                agent_persona_id=persona.id,
                follower_count=0,
            )
            db.add(agent_user)
            await db.flush()

            post_content = SAMPLE_POSTS[AGENT_PERSONAS.index(persona_data) % len(SAMPLE_POSTS)]
            post = Post(user_id=agent_user.id, content=post_content)
            db.add(post)

            print(f"✓ Seeded agent: {persona_data['name']}")

        await db.commit()


async def main():
    print("Initialising NOVA database...")
    await create_tables()
    await seed_agents()
    print("\n✓ NOVA is ready.")
    print("  Run: uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    asyncio.run(main())
