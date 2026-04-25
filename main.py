from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import engine, Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="NOVA API",
    description="Agentic Social Media Platform — Made by Bharath",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc), "code": "internal_error"})


from routers import auth, posts, comments, feed, users, notifications

PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(posts.router, prefix=PREFIX)
app.include_router(comments.router, prefix=PREFIX)
app.include_router(feed.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(notifications.router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "NOVA", "made_by": "Bharath"}
