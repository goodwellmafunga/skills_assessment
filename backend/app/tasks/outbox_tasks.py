from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.assessment import OutboxEvent
from app.core.events import ws_manager


@celery_app.task(name="app.tasks.outbox_tasks.dispatch_outbox", bind=True, max_retries=3)
def dispatch_outbox(self):
    asyncio.run(_dispatch())


async def _dispatch():
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        rows = await db.execute(
            select(OutboxEvent).where(OutboxEvent.processed.is_(False)).order_by(OutboxEvent.id.asc()).limit(100)
        )
        events = rows.scalars().all()
        for ev in events:
            await ws_manager.broadcast({"type": ev.event_type, "payload": ev.payload})
            ev.processed = True
        await db.commit()
