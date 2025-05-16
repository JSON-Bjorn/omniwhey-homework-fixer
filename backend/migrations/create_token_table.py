"""
Migration script for creating the tokens table for database authentication.

This script defines the SQL operations needed to:
1. Create a tokens table for database-based authentication
2. Add relationships between users and tokens
"""

from sqlalchemy import (
    text,
    MetaData,
)
import uuid


def upgrade_sql():
    """Return SQL statements to upgrade the database."""
    return [
        # Create the tokens table
        """
        CREATE TABLE tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """,
        # Create an index for faster token lookups
        """
        CREATE INDEX idx_tokens_token ON tokens(token);
        """,
        # Create an index for user_id to optimize queries for user's tokens
        """
        CREATE INDEX idx_tokens_user_id ON tokens(user_id);
        """,
    ]


def downgrade_sql():
    """Return SQL statements to downgrade the database."""
    return [
        # Drop the tokens table
        """
        DROP TABLE IF EXISTS tokens;
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
