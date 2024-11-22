import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException
from main import app  # Assure-toi que l'importation de l'app FastAPI est correcte

# Fixture pour gérer la boucle d'événements pour pytest
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_register_user():
    user_data = {
        "email": "test@example.com",
        "password": "password1234",
        "first_name": "Michel",
        "last_name": "Leclerc",
        "address": "123 rue de la paix",
        "phone_number": "123-456-7890"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/users/", json=user_data)

    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_login_user():
    user_data = {
        "email": "test@example.com",
        "password": "password1234",
        "first_name": "Michel",
        "last_name": "Leclerc",
        "address": "123 rue de la paix",
        "phone_number": "123-456-7890"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/users/", json=user_data)

    login_data = {"username": "test@example.com", "password": "password1234"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/login", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_user_invalid():
    login_data = {"username": "wrong@example.com", "password": "wrongpassword"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/login", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_hello_world():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
