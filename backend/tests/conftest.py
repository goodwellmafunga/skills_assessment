import os
import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from asgi_lifespan import LifespanManager


import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager



# IMPORTANT: import your FastAPI app
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    # Adjust these as needed for your local test DB
    os.environ.setdefault("ENV", "test")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:1234@localhost:5432/chatbot",  # <- your working DB URL
    )
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
