"""
Script to run all database migrations in sequence.

This script executes all migrations in the correct order to set up or update the database.
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
from migrations.user_id_to_uuid_migration import upgrade_sql as uuid_migration
from migrations.create_token_table import upgrade_sql as token_table_migration
from migrations.update_user_active_default import (
    upgrade_sql as active_migration,
)
from migrations.add_token_types import upgrade_sql as token_types_migration
from migrations.create_features_table import upgrade_sql as features_migration


async def run_all_migrations():
    """Run all migrations in sequence."""
    # Create engine
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=True,  # Set to True to see SQL statements
    )

    migrations = [
        ("User ID to UUID", uuid_migration),
        ("Token Table Creation", token_table_migration),
        ("User Active Default", active_migration),
        ("Token Types", token_types_migration),
        ("Features Table", features_migration),
    ]

    # Execute all migrations
    print("Starting all migrations...")

    async with engine.begin() as conn:
        for migration_name, migration_func in migrations:
            print(f"\n=== Running {migration_name} migration ===")
            statements = migration_func()

            for i, stmt in enumerate(statements, start=1):
                try:
                    print(f"Executing step {i} of {migration_name}...")
                    await conn.execute(text(stmt))
                    print(f"Step {i} completed successfully.")
                except Exception as e:
                    print(f"Error in {migration_name}, step {i}: {e}")
                    print("Continuing with next migration...")
                    break  # Move to next migration if one fails

    print("\nAll migrations completed!")


if __name__ == "__main__":
    asyncio.run(run_all_migrations())
