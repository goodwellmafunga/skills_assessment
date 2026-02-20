# backend/seed_question_bank.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text as sql_text

from app.core.config import settings
from app.models.question import Question, QuestionOption

SCORE_BY_LABEL = {"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}

QUESTION_BANK = [
    # ---------------- SOFT SKILLS ----------------
    {
        "domain": "soft",
        "category": "Communication",
        "text": "When you have to give feedback to a team member about a mistake they made, you usually:",
        "options": [
            ("a", "Speak with them privately and explain clearly what went wrong"),
            ("b", "Send a brief message pointing out the error"),
            ("c", "Mention it casually during a team meeting"),
            ("d", "Wait to see if they notice it themselves"),
            ("e", "Ask someone else to talk to them"),
        ],
    },
    {
        "domain": "soft",
        "category": "Communication",
        "text": "If you need to explain a complex new policy to your team, you are most likely to:",
        "options": [
            ("a", "Prepare a short presentation and leave time for questions"),
            ("b", "Send an email with detailed notes"),
            ("c", "Explain it briefly and offer to clarify if needed"),
            ("d", "Share a document and assume they will read it"),
            ("e", "Avoid explaining unless someone asks"),
        ],
    },
    {
        "domain": "soft",
        "category": "Problem-Solving",
        "text": "When you face a work challenge with no clear solution, your first step is usually to:",
        "options": [
            ("a", "Break the problem into parts and research each one"),
            ("b", "Discuss with colleagues to gather ideas"),
            ("c", "Try the first idea that comes to mind"),
            ("d", "Look for similar past situations for guidance"),
            ("e", "Wait for instructions from a supervisor"),
        ],
    },
    {
        "domain": "soft",
        "category": "Problem-Solving",
        "text": "If a project is delayed due to an unexpected issue, you:",
        "options": [
            ("a", "Analyze the cause and propose a new timeline"),
            ("b", "Gather the team to brainstorm solutions"),
            ("c", "Work extra hours to catch up"),
            ("d", "Hope the issue resolves on its own"),
            ("e", "Report it to your manager without suggestions"),
        ],
    },
    {
        "domain": "soft",
        "category": "Adaptability & Flexibility",
        "text": "Your workplace introduces a new required software. You:",
        "options": [
            ("a", "Start learning it immediately and explore all features"),
            ("b", "Follow the training provided step-by-step"),
            ("c", "Use only the basics needed to get by"),
            ("d", "Stick to the old system if possible"),
            ("e", "Avoid using it until absolutely necessary"),
        ],
    },
    {
        "domain": "soft",
        "category": "Adaptability & Flexibility",
        "text": "If your manager suddenly changes a deadline, you typically:",
        "options": [
            ("a", "Adjust your schedule right away and inform your team"),
            ("b", "Feel stressed but try to adapt"),
            ("c", "Ask for help to meet the new deadline"),
            ("d", "Complain about the change"),
            ("e", "Ignore the new deadline and work at your own pace"),
        ],
    },
    {
        "domain": "soft",
        "category": "Time Management",
        "text": "At the start of a busy workday, you usually:",
        "options": [
            ("a", "List all tasks and prioritize the most important"),
            ("b", "Tackle tasks in the order they arrive"),
            ("c", "Work on whatever feels urgent at the moment"),
            ("d", "Jump between tasks throughout the day"),
            ("e", "Struggle to decide where to begin"),
        ],
    },
    {
        "domain": "soft",
        "category": "Time Management",
        "text": "When you have multiple assignments with similar deadlines, you:",
        "options": [
            ("a", "Plan daily goals to finish each on time"),
            ("b", "Focus on one until it’s done, then move to the next"),
            ("c", "Work a little on each every day"),
            ("d", "Rush to finish all near the deadline"),
            ("e", "Ask for extensions on some tasks"),
        ],
    },
    {
        "domain": "soft",
        "category": "Networking",
        "text": "At a professional event, when you meet someone new, you usually:",
        "options": [
            ("a", "Introduce yourself and ask about their work"),
            ("b", "Exchange contact information for future connection"),
            ("c", "Chat politely but not about work topics"),
            ("d", "Stay with people you already know"),
            ("e", "Keep to yourself and avoid conversations"),
        ],
    },
    {
        "domain": "soft",
        "category": "Networking",
        "text": "If you need advice on a work topic outside your expertise, you:",
        "options": [
            ("a", "Reach out to a professional contact for guidance"),
            ("b", "Search for experts online and connect with them"),
            ("c", "Ask someone in your department"),
            ("d", "Try to figure it out alone"),
            ("e", "Skip that part of the task"),
        ],
    },

    # ---------------- DIGITAL SKILLS ----------------
    {
        "domain": "digital",
        "category": "Digital Communication",
        "text": "How do you most often communicate with colleagues during work?",
        "options": [
            ("a", "Through email, chat apps, and video calls as needed"),
            ("b", "Mainly email, sometimes phone calls"),
            ("c", "Mostly in-person or phone, rarely digital tools"),
            ("d", "Only when someone contacts me first"),
            ("e", "I avoid digital communication when possible"),
        ],
    },
    {
        "domain": "digital",
        "category": "Digital Communication",
        "text": "When you receive an important work message online, you usually:",
        "options": [
            ("a", "Reply promptly and clearly"),
            ("b", "Read it and reply later when convenient"),
            ("c", "Acknowledge it with a quick response"),
            ("d", "Wait to see if follow-up is needed"),
            ("e", "Often miss or forget to respond"),
        ],
    },
    {
        "domain": "digital",
        "category": "Data Management and Analysis",
        "text": "If you need to organize project data, you typically:",
        "options": [
            ("a", "Use software like Excel or databases to sort and analyze"),
            ("b", "Create simple lists or tables"),
            ("c", "Write notes on paper"),
            ("d", "Ask someone else to organize it"),
            ("e", "Avoid dealing with data altogether"),
        ],
    },
    {
        "domain": "digital",
        "category": "Data Management and Analysis",
        "text": "When making a decision based on numbers or reports, you:",
        "options": [
            ("a", "Review the data, look for trends, and draw conclusions"),
            ("b", "Check the main figures and trust your judgment"),
            ("c", "Rely on summaries from others"),
            ("d", "Go with your intuition"),
            ("e", "Prefer not to use data in decisions"),
        ],
    },
    {
        "domain": "digital",
        "category": "Use of Technology",
        "text": "When given a new digital tool at work, you:",
        "options": [
            ("a", "Explore it fully and try to master all functions"),
            ("b", "Learn the features needed for your tasks"),
            ("c", "Use only what you already know"),
            ("d", "Stick to older methods if allowed"),
            ("e", "Avoid using it unless required"),
        ],
    },
    {
        "domain": "digital",
        "category": "Use of Technology",
        "text": "If a device or software isn’t working properly, you first:",
        "options": [
            ("a", "Try to troubleshoot using online resources"),
            ("b", "Restart it or follow basic steps you know"),
            ("c", "Ask a colleague for help"),
            ("d", "Report it to IT and wait"),
            ("e", "Stop using it until it’s fixed"),
        ],
    },
    {
        "domain": "digital",
        "category": "Cybersecurity Awareness",
        "text": "How do you handle passwords for work accounts?",
        "options": [
            ("a", "Use strong, unique passwords and change them regularly"),
            ("b", "Use a mix of letters and numbers"),
            ("c", "Use simple passwords easy to remember"),
            ("d", "Use the same password for many accounts"),
            ("e", "Write passwords down where others might see"),
        ],
    },
    {
        "domain": "digital",
        "category": "Cybersecurity Awareness",
        "text": "If you get an email from an unknown sender with a link, you:",
        "options": [
            ("a", "Delete it without opening"),
            ("b", "Check the sender’s name and email address first"),
            ("c", "Open but don’t click anything"),
            ("d", "Click if the topic looks interesting"),
            ("e", "Forward it to others to check"),
        ],
    },
    {
        "domain": "digital",
        "category": "Digital Literacy for Innovation",
        "text": "When you need to learn something new for your job, you usually:",
        "options": [
            ("a", "Search online for tutorials, courses, or videos"),
            ("b", "Ask a coworker to show you"),
            ("c", "Wait for formal training"),
            ("d", "Try to learn from a manual or guide"),
            ("e", "Avoid learning new things unless forced"),
        ],
    },
    {
        "domain": "digital",
        "category": "Digital Literacy for Innovation",
        "text": "If you hear about a useful new app for work, you:",
        "options": [
            ("a", "Try it out and see if it helps your productivity"),
            ("b", "Read reviews and maybe try later"),
            ("c", "Stick with what you already use"),
            ("d", "Wait until your workplace officially adopts it"),
            ("e", "Ignore it"),
        ],
    },
]

async def main():
    db_url = settings.DATABASE_URL
    if not db_url:
        raise RuntimeError("settings.DATABASE_URL is empty. Check your .env POSTGRES_* or DATABASE_URL")

    engine = create_async_engine(db_url, future=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        q_table = Question.__tablename__
        o_table = QuestionOption.__tablename__

        # wipe clean
        await session.execute(
            sql_text(f'TRUNCATE TABLE "{o_table}", "{q_table}" RESTART IDENTITY CASCADE;')
        )

        # insert
        for i, q in enumerate(QUESTION_BANK, start=1):
            question = Question(
                text=q["text"].strip(),
                domain=q["domain"],
                category=q["category"].strip(),
                display_order=i,
                is_active=True,
            )
            for label, opt_text in q["options"]:
                lbl = label.strip().lower()
                question.options.append(
                    QuestionOption(
                        label=lbl,
                        text=opt_text.strip(),
                        score=SCORE_BY_LABEL[lbl],
                    )
                )
            session.add(question)

        await session.commit()

    await engine.dispose()
    print(f"✅ Seeded {len(QUESTION_BANK)} questions")

if __name__ == "__main__":
    asyncio.run(main())
