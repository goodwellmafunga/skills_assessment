def generate_recommendations(category_scores: dict[str, float]) -> list[dict]:
    recs: list[dict] = []

    for category, score in category_scores.items():
        if score < 2.5:
            recs.append({
                "skill_area": category,
                "priority": "high",
                "message": f"Urgent upskilling needed in {category}. Recommend immediate targeted training.",
            })
        elif score < 3.5:
            recs.append({
                "skill_area": category,
                "priority": "medium",
                "message": f"Development needed in {category}. Recommend practical workshops and coaching.",
            })

    if not recs:
        recs.append({
            "skill_area": "overall",
            "priority": "low",
            "message": "Strong skill profile. Continue with advanced learning pathways.",
        })

    return recs
