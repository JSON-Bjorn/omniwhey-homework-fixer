"""
Migration script for adding token types to the tokens table.

This script defines the SQL operations needed to:
1. Add a token_type column to the tokens table
2. Set default token type to 'access'
3. Create an index on the token_type column
"""

from sqlalchemy import text


def upgrade_sql():
    """Return SQL statements to upgrade the database."""
    return [
        # Add token_type column with default value 'access'
        """
        ALTER TABLE tokens
        ADD COLUMN token_type VARCHAR(20) NOT NULL DEFAULT 'access'
        """,
        # Create an index on token_type for faster queries
        """
        CREATE INDEX idx_tokens_token_type ON tokens (token_type)
        """,
    ]


def downgrade_sql():
    """Return SQL statements to downgrade the database."""
    return [
        # Drop the index first
        """
        DROP INDEX IF EXISTS idx_tokens_token_type
        """,
        # Drop the token_type column
        """
        ALTER TABLE tokens DROP COLUMN token_type
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
