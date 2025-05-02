#!/usr/bin/env python3
"""
Standalone database initialization script that doesn't rely on other modules.
Use this when the main init_db.py script fails due to import errors.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import time

# Get database connection settings from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "omniwhey")

# Detect if running in Docker
docker_mode = DB_HOST == "db"
print(f"Docker mode detected: {docker_mode}")


def wait_for_database(max_retries=10, retry_interval=3):
    """Wait for the database server to be available."""
    retries = 0
    while retries < max_retries:
        try:
            print(
                f"Attempting to connect to database server (attempt {retries + 1}/{max_retries})..."
            )
            if docker_mode:
                # In Docker, we need to check if the container is ready
                result = subprocess.run(
                    ["pg_isready", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER],
                    capture_output=True,
                    text=True,
                )
                if "accepting connections" in result.stdout:
                    print("✅ Database server is accepting connections!")
                    return True
            else:
                # Try direct connection
                conn = psycopg2.connect(
                    user=DB_USER,
                    password=DB_PASSWORD,
                    host=DB_HOST,
                    port=DB_PORT,
                    connect_timeout=5,
                )
                conn.close()
                print("✅ Database server connection successful!")
                return True
        except Exception as e:
            print(f"❌ Failed to connect to database server: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)

    print("Could not connect to the database server after multiple attempts.")
    return False


def init_db():
    """Initialize the database without relying on other modules."""
    try:
        if not wait_for_database():
            return False

        # Always use direct database connection method regardless of mode
        return _init_db_local()
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


def _init_db_docker():
    """Initialize database using Docker commands."""
    try:
        print("Using Docker to initialize database...")

        # Try using docker exec to create/ensure database exists
        create_db_cmd = [
            "docker",
            "exec",
            "-i",
            "docker-db-1",
            "psql",
            "-U",
            DB_USER,
            "-c",
            f"CREATE DATABASE {DB_NAME} WITH OWNER {DB_USER};",
        ]

        try:
            result = subprocess.run(create_db_cmd, capture_output=True, text=True)
            if "already exists" in result.stderr:
                print(f"Database '{DB_NAME}' already exists")
            elif result.returncode == 0:
                print(f"Database '{DB_NAME}' created successfully")
            else:
                print(f"Docker command output: {result.stdout}")
                print(f"Docker command error: {result.stderr}")
                print("Continuing anyway...")
        except Exception as e:
            print(f"Error creating database: {e}")
            print("Continuing with table creation...")

        # Now use Docker to create tables
        print("Creating database tables via Docker...")

        # Create users table
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
        """

        # Create a temporary SQL file
        sql_file = Path("./create_tables.sql")
        with open(sql_file, "w") as f:
            f.write(users_table_sql)

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

        print("Database initialization completed.")
        return True

    except Exception as docker_error:
        print(f"Error using Docker command: {docker_error}")
        return False


def _init_db_local():
    """Initialize database using local connection."""
    try:
        print("Using local connection to initialize database...")

        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
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

        # Commit changes
        db_conn.commit()

        # Close connection
        db_cursor.close()
        db_conn.close()

        print("Database initialization completed.")
        return True

    except Exception as e:
        print(f"Error initializing local database: {e}")
        return False


if __name__ == "__main__":
    print("\n========== STANDALONE DATABASE INITIALIZATION ==========\n")
    print(f"Database target: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    success = init_db()
    if success:
        print("\n✅ Database setup complete!")
    else:
        print("\n❌ Failed to initialize database")
        sys.exit(1)
