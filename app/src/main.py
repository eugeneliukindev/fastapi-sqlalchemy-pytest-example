from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Annotated
from src.database.manager import db_manager
from src.core.models import Post
from src.core.models import User
from src.core.schemas.post import PostOut
from src.core.schemas.user import UserCreate, UserOut

app = FastAPI(title="Minimal Blog API")


SessionDep = Annotated[AsyncSession, Depends(db_manager.session_getter)]


@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: SessionDep):
    user = User(name=user_data.name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, session: SessionDep):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@app.get("/users/{user_id}/posts", response_model=List[PostOut])
async def get_user_posts(user_id: int, session: SessionDep):
    result = await session.execute(
        select(User).where(User.id == user_id).options(selectinload(User.posts))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user.posts


@app.get("/posts/{post_id}", response_model=PostOut)
async def get_post(post_id: int, session: SessionDep):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post
