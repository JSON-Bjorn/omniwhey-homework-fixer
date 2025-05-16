"""
Script to execute the token table migration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from migrations.create_token_table import upgrade_sql


async def run_migration():
    """Run the migration to create the tokens table."""
    # Create engine
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=True,  # Set to True to see SQL statements
    )

    # Execute the migration
    print("Starting token table migration...")
    async with engine.begin() as conn:
        for i, stmt in enumerate(upgrade_sql(), start=1):
            print(f"Executing step {i}...")
            try:
                await conn.execute(text(stmt))
                print(f"Step {i} completed successfully.")
            except Exception as e:
                print(f"Error in step {i}: {e}")
                raise

    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_migration())
