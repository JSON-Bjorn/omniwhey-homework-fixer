"""
Migration script for updating the default value of is_active in the users table.

This script defines the SQL operations needed to:
1. Change the default value of is_active column from TRUE to FALSE for new users
2. This ensures users must verify their email before being activated
"""

from sqlalchemy import text


def upgrade_sql():
    """Return SQL statements to upgrade the database."""
    return [
        # Change default value of is_active to FALSE
        """
        ALTER TABLE users
        ALTER COLUMN is_active SET DEFAULT FALSE
        """,
        # Ensure is_verified column exists with correct default
        # This is to make sure the column is present in case it wasn't added before
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'is_verified'
            ) THEN
                ALTER TABLE users
                ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;
            END IF;
        END $$;
        """,
    ]


def downgrade_sql():
    """Return SQL statements to downgrade the database."""
    return [
        # Restore default value of is_active to TRUE
        """
        ALTER TABLE users
        ALTER COLUMN is_active SET DEFAULT TRUE
        """,
    ]


def run_migration(conn):
    """Execute the migration steps."""
    for stmt in upgrade_sql():
        conn.execute(text(stmt))


def rollback_migration(conn):
    """Rollback the migration steps."""
    for stmt in downgrade_sql():
        conn.execute(text(stmt))
