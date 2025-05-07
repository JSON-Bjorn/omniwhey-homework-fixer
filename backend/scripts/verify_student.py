import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from sqlalchemy import update
from app.db.session import async_session_factory
from app.models import User


async def mark_verified():
    """Mark student with ID 2 as verified."""
    async with async_session_factory() as session:
        await session.execute(
            update(User).where(User.id == 2).values(is_verified=True)
        )
        await session.commit()
        print("Student verified successfully")


if __name__ == "__main__":
    asyncio.run(mark_verified())
