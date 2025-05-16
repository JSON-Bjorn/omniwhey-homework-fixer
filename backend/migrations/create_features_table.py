"""
Migration script for creating a feature flags table.

This script defines the SQL operations needed to:
1. Create a features table for feature flags
2. Add initial feature flags
"""

from sqlalchemy import text


def upgrade_sql():
    """Return SQL statements to upgrade the database."""
    return [
        # Create features table
        """
        CREATE TABLE features (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            enabled BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """,
        # Add initial feature flags
        """
        INSERT INTO features (name, description, enabled)
        VALUES 
            ('email_verification', 'Require email verification before login', TRUE),
            ('ai_grading', 'Use AI for automated grading of student assignments', FALSE),
            ('template_approval', 'Require teacher approval of AI-generated templates', TRUE)
        """,
    ]


def downgrade_sql():
    """Return SQL statements to downgrade the database."""
    return [
        # Drop the features table
        """
        DROP TABLE IF EXISTS features
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
