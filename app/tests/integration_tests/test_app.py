from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.model_factories import UserFactory, PostFactory
import pytest
from fastapi import status
from fastapi import HTTPException


async def _check_http_exception(
    client: AsyncClient, url: str, exception: HTTPException
) -> None:
    response = await client.get(url)
    assert response.status_code == exception.status_code
    assert response.json()["detail"] == exception.detail


@pytest.mark.integration
async def test_create_user_and_get_it(client: AsyncClient, session: AsyncSession):
    response = await client.post("/users/", json={"name": "Victoria"})
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Victoria"
    assert "id" in created

    response = await client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Victoria"

    non_existent_id = 999999
    await _check_http_exception(
        client=client,
        url=f"/users/{non_existent_id}",
        exception=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )


@pytest.mark.integration
async def test_user_with_posts(session: AsyncSession, client: AsyncClient):
    user = UserFactory.create(name="Maxim")
    PostFactory.create_batch(4, user=user)
    await session.commit()

    response = await client.get(f"/users/{user.id}/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 4
    assert all(p["user_id"] == user.id for p in posts)

    non_existent_id = 999999
    await _check_http_exception(
        client=client,
        url=f"/users/{non_existent_id}/posts",
        exception=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )


@pytest.mark.integration
async def test_empty_user_posts(session: AsyncSession, client: AsyncClient):
    user = UserFactory.create(name="EmptyUser")
    await session.commit()

    response = await client.get(f"/users/{user.id}/posts")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
async def test_post_detail(session: AsyncSession, client: AsyncClient):
    user = UserFactory.create()
    post = PostFactory.create(user=user, title="Very important article about testing")
    await session.commit()

    response = await client.get(f"/posts/{post.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Very important article about testing"
    assert data["user_id"] == user.id

    non_existent_id = 999999
    await _check_http_exception(
        client=client,
        url=f"/posts/{non_existent_id}",
        exception=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        ),
    )
