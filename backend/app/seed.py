import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.question import Question, QuestionOption

DEFAULT_QUESTIONS = [
    {
        "text": "I communicate clearly and respectfully in professional settings.",
        "domain": "soft",
        "category": "communication",
        "display_order": 1,
    },
    {
        "text": "I can use spreadsheets to organize and analyze data.",
        "domain": "digital",
        "category": "data literacy",
        "display_order": 2,
    },
]

OPTIONS = [
    ("A", "Always", 5),
    ("B", "Often", 4),
    ("C", "Sometimes", 3),
    ("D", "Rarely", 2),
    ("E", "Never", 1),
]


async def main():
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        for q in DEFAULT_QUESTIONS:
            question = Question(**q, is_active=True)
            for label, text, score in OPTIONS:
                question.options.append(QuestionOption(label=label, text=text, score=score))
            db.add(question)
        await db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
