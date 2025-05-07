"""
Database initialization and utility functions.
"""

import os
import sys
import subprocess
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from passlib.context import CryptContext

# Add the backend directory to the path for imports
backend_path = Path(__file__).resolve().parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from config.database import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, docker_mode
from models.models import Base, User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    """Initialize the database, creating tables if they don't exist."""
    try:
        if docker_mode:
            return _init_db_docker()
        else:
            return _init_db_local()
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Make sure PostgreSQL is running on your local machine or in Docker")
        return False


def _init_db_docker():
    """Initialize database using Docker commands."""
    try:
        print("Using Docker to initialize database...")

        # Try using docker exec to create/ensure database exists
        create_db_cmd = [
            "docker",
            "exec",
            "docker-db-1",
            "psql",
            "-U",
            DB_USER,
            "-c",
            f"CREATE DATABASE {DB_NAME} WITH OWNER {DB_USER};",
        ]
        result = subprocess.run(create_db_cmd, capture_output=True, text=True)

        if "already exists" in result.stderr:
            print(f"Database '{DB_NAME}' already exists")
        elif result.returncode == 0:
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Docker command output: {result.stdout}")
            print(f"Docker command error: {result.stderr}")

        # Now use Docker to create tables
        print("Creating database tables via Docker...")

        # Create users table
        users_table_sql = f"""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """

        # Create tokens table
        tokens_table_sql = f"""
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            is_revoked BOOLEAN DEFAULT FALSE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """

        # Create submissions table
        submissions_table_sql = f"""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            file_path VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending',
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """

        # Create feedback table
        feedback_table_sql = f"""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            grade VARCHAR(50),
            submission_id INTEGER REFERENCES submissions(id) ON DELETE CASCADE UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """

        # Combine all SQL commands
        all_tables_sql = (
            users_table_sql
            + tokens_table_sql
            + submissions_table_sql
            + feedback_table_sql
        )

        # Save SQL to a temporary file
        sql_file = Path(backend_path) / "create_tables.sql"
        with open(sql_file, "w") as f:
            f.write(all_tables_sql)

        # Execute the SQL file in the Docker container
        exec_sql_cmd = [
            "docker",
            "exec",
            "-i",
            "docker-db-1",
            "psql",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
        ]

        with open(sql_file, "r") as f:
            result = subprocess.run(
                exec_sql_cmd, stdin=f, capture_output=True, text=True
            )

        # Clean up temp file
        os.remove(sql_file)

        if result.returncode == 0:
            print("Database tables created successfully")
            return True
        else:
            print(f"Error creating tables: {result.stderr}")
            return False

    except Exception as docker_error:
        print(f"Error using Docker command: {docker_error}")
        print("Make sure Docker is running and the database container is up")
        return False


def _init_db_local():
    """Initialize database using local connection."""
    try:
        print("Using local connection to initialize database...")

        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Create a cursor
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()

        if not exists:
            # Create database
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")

        # Close connection to PostgreSQL server
        cursor.close()
        conn.close()

        # Now connect to the database and create tables
        db_conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
        db_cursor = db_conn.cursor()

        # Create tables
        db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """)

        db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            is_revoked BOOLEAN DEFAULT FALSE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)

        db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            file_path VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending',
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """)

        db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            grade VARCHAR(50),
            submission_id INTEGER REFERENCES submissions(id) ON DELETE CASCADE UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """)

        # Commit changes
        db_conn.commit()

        # Close connection
        db_cursor.close()
        db_conn.close()

        print("Database tables created successfully")
        return True

    except Exception as e:
        print(f"Error initializing local database: {e}")
        return False


def seed_db():
    """Seed the database with initial test data."""
    try:
        # Test user credentials
        test_user_email = "user@example.com"
        test_user_password = "password123"
        hashed_password = pwd_context.hash(test_user_password)

        if docker_mode:
            return _seed_db_docker(test_user_email, hashed_password)
        else:
            return _seed_db_local(test_user_email, hashed_password)

    except Exception as e:
        print(f"Error seeding database: {e}")
        return False


def _seed_db_docker(email, hashed_password):
    """Seed database using Docker commands."""
    try:
        seed_sql = f"""
        INSERT INTO users (email, hashed_password, is_active) 
        VALUES ('{email}', '{hashed_password}', TRUE) 
        ON CONFLICT (email) DO NOTHING;
        """

        sql_file = Path(backend_path) / "seed_db.sql"
        with open(sql_file, "w") as f:
            f.write(seed_sql)

        cmd = [
            "docker",
            "exec",
            "-i",
            "docker-db-1",
            "psql",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
        ]

        with open(sql_file, "r") as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)

        # Clean up temp file
        os.remove(sql_file)

        if result.returncode == 0:
            print(f"Test user '{email}' created or already exists")
            return True
        else:
            print(f"Error creating test user: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error seeding Docker database: {e}")
        return False


def _seed_db_local(email, hashed_password):
    """Seed database using local connection."""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
        cursor = conn.cursor()

        # Insert test user with ON CONFLICT DO NOTHING
        cursor.execute(f"""
        INSERT INTO users (email, hashed_password, is_active) 
        VALUES ('{email}', '{hashed_password}', TRUE) 
        ON CONFLICT (email) DO NOTHING;
        """)

        # Commit changes
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()

        print(f"Test user '{email}' created or already exists")
        print(f"  Email: {email}")
        print(f"  Password: password123")
        return True

    except Exception as e:
        print(f"Error seeding local database: {e}")
        return False
