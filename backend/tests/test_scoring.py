from app.services.recommendation_service import generate_recommendations


def test_generate_recommendations_high_priority():
    out = generate_recommendations({"communication": 2.2, "teamwork": 3.8})
    assert any(r["priority"] == "high" for r in out)
