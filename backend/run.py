#!/usr/bin/env python3
"""
Main entry point for the OmniWhey API application.
This file ensures imports work correctly in all environments (local development and Docker).
"""

import os
import sys
import time
from pathlib import Path
import psycopg2

# Ensure the backend directory is in the path for proper imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import necessary modules
from config.database import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from app.main import app  # Import app at module level for proper health checks


def wait_for_database(max_retries=10, retry_interval=3):
    """Wait for the database to become available, with a finite number of retries."""
    retries = 0
    while retries < max_retries:
        try:
            print(
                f"Attempting to connect to database at {DB_HOST}:{DB_PORT} (attempt {retries + 1}/{max_retries})..."
            )
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                connect_timeout=5,
            )
            conn.close()
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(
                    f"Maximum retries ({max_retries}) reached. Please check your database configuration."
                )

    print("Could not connect to the database after multiple attempts.")
    return False


# This can be run directly with: python run.py
# Or with uvicorn: uvicorn run:app --reload
if __name__ == "__main__":
    import uvicorn

    # Load port from environment or use default
    port = int(os.getenv("PORT", "8000"))

    # Optional: wait for database to be available
    # In production, you might want to comment this out and rely on
    # the database initialization step in docker-compose
    if os.getenv("WAIT_FOR_DB", "true").lower() == "true":
        db_ready = wait_for_database()
        if not db_ready and os.getenv("REQUIRE_DB", "false").lower() == "true":
            print("Database connection required but not available. Exiting.")
            sys.exit(1)

    print(f"Starting OmniWhey API Server at http://0.0.0.0:{port}")
    print(f"API Documentation available at http://0.0.0.0:{port}/api/swagger")

    # Start the server
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
