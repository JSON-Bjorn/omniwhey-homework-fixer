"""
Migration script to change user ID from integer to UUID.

This script defines the SQL operations needed to:
1. Add UUID columns to users and related tables
2. Populate UUIDs for existing records
3. Drop integer ID columns and rename UUID columns
4. Recreate foreign keys and indexes
"""

from sqlalchemy import (
    text,
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

# SQL operations for the migration


def upgrade_sql():
    """Return SQL statements to upgrade the database."""
    return [
        # 1. Add UUID columns to users table
        """
        ALTER TABLE users 
        ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid() NOT NULL
        """,
        # 2. Add UUID columns to association tables
        """
        ALTER TABLE teacher_student_associations
        ADD COLUMN teacher_uuid_id UUID NOT NULL,
        ADD COLUMN student_uuid_id UUID NOT NULL
        """,
        # 3. Add UUID column to student_assignments table
        """
        ALTER TABLE student_assignments
        ADD COLUMN student_uuid_id UUID NOT NULL
        """,
        # 4. Add UUID column to assignments table
        """
        ALTER TABLE assignments
        ADD COLUMN teacher_uuid_id UUID NOT NULL
        """,
        # 5. Update the UUID columns with the corresponding user IDs
        """
        UPDATE teacher_student_associations tsa
        SET teacher_uuid_id = u.uuid_id
        FROM users u
        WHERE tsa.teacher_id = u.id
        """,
        """
        UPDATE teacher_student_associations tsa
        SET student_uuid_id = u.uuid_id
        FROM users u
        WHERE tsa.student_id = u.id
        """,
        """
        UPDATE student_assignments sa
        SET student_uuid_id = u.uuid_id
        FROM users u
        WHERE sa.student_id = u.id
        """,
        """
        UPDATE assignments a
        SET teacher_uuid_id = u.uuid_id
        FROM users u
        WHERE a.teacher_id = u.id
        """,
        # 6. Drop the primary key constraints and foreign key constraints
        """
        ALTER TABLE teacher_student_associations
        DROP CONSTRAINT teacher_student_associations_pkey,
        DROP CONSTRAINT teacher_student_associations_teacher_id_fkey,
        DROP CONSTRAINT teacher_student_associations_student_id_fkey
        """,
        """
        ALTER TABLE student_assignments
        DROP CONSTRAINT student_assignments_student_id_fkey
        """,
        """
        ALTER TABLE assignments
        DROP CONSTRAINT assignments_teacher_id_fkey
        """,
        # 7. Drop the old integer columns
        """
        ALTER TABLE teacher_student_associations
        DROP COLUMN teacher_id,
        DROP COLUMN student_id
        """,
        """
        ALTER TABLE student_assignments
        DROP COLUMN student_id
        """,
        """
        ALTER TABLE assignments
        DROP COLUMN teacher_id
        """,
        # 8. Rename the UUID columns
        """
        ALTER TABLE teacher_student_associations
        RENAME COLUMN teacher_uuid_id TO teacher_id,
        RENAME COLUMN student_uuid_id TO student_id
        """,
        """
        ALTER TABLE student_assignments
        RENAME COLUMN student_uuid_id TO student_id
        """,
        """
        ALTER TABLE assignments
        RENAME COLUMN teacher_uuid_id TO teacher_id
        """,
        # 9. Create a new primary key constraint for users table
        """
        ALTER TABLE users
        DROP CONSTRAINT users_pkey,
        ALTER COLUMN id DROP NOT NULL
        """,
        """
        ALTER TABLE users
        RENAME COLUMN id TO old_id,
        RENAME COLUMN uuid_id TO id,
        ADD PRIMARY KEY (id)
        """,
        # 10. Create new primary key and foreign key constraints
        """
        ALTER TABLE teacher_student_associations
        ADD PRIMARY KEY (teacher_id, student_id),
        ADD CONSTRAINT teacher_student_associations_teacher_id_fkey 
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
        ADD CONSTRAINT teacher_student_associations_student_id_fkey 
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE student_assignments
        ADD CONSTRAINT student_assignments_student_id_fkey 
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        """,
        """
        ALTER TABLE assignments
        ADD CONSTRAINT assignments_teacher_id_fkey 
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        """,
        # 11. Optional: Drop the old id column from users after ensuring everything works
        # Uncomment this if you're sure the migration worked correctly
        # """
        # ALTER TABLE users
        # DROP COLUMN old_id
        # """,
    ]


def downgrade_sql():
    """Return SQL statements to downgrade the database."""
    return [
        # Restore the original structure (not detailed here as it's complex)
        # This should only be used if absolutely necessary
        """
        -- Downgrade operations would go here
        """
    ]


def run_migration(conn):
    """Execute the migration steps."""
    for stmt in upgrade_sql():
        conn.execute(text(stmt))


def rollback_migration(conn):
    """Rollback the migration steps."""
    for stmt in downgrade_sql():
        conn.execute(text(stmt))
