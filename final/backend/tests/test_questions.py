import uuid

import pytest


@pytest.mark.anyio
async def test_list_questions(client):
    r = await client.get("/api/v1/questions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_create_question_requires_admin(client):
    payload = {
        "text": f"Test question {uuid.uuid4()}",
        "domain": "soft",
        "category": "communication",
        "display_order": 0,
        "is_active": True,
        "options": [
            {"label": "A", "text": "Strongly agree", "score": 5},
            {"label": "B", "text": "Agree", "score": 4},
        ],
    }

    r = await client.post("/api/v1/questions", json=payload)
    # should be blocked without token/admin
    assert r.status_code in (401, 403)
