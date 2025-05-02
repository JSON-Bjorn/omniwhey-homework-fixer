#!/usr/bin/env python3
"""
Database initialization script.
This creates and seeds the database for the OmniWhey application.
"""

import sys
from pathlib import Path

# Add the current directory to the path
backend_path = Path(__file__).resolve().parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from config.database import DB_HOST, DB_PORT, DB_NAME
from app.utils.db_utils import init_db, seed_db


def main():
    print("\n========== DATABASE INITIALIZATION ==========\n")
    print(f"Database target: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    # Check if running in Docker
    docker_mode = DB_HOST == "db"
    print(f"Docker mode detected: {docker_mode}")

    print("\nStep 1: Creating database and tables...")

    db_initialized = init_db()

    if db_initialized:
        print("\nStep 2: Seeding database with test data...")
        seed_success = seed_db()

        if seed_success:
            print("\n✅ Database setup complete!")
            return True
        else:
            print("\n❌ Failed to seed database")
            return False
    else:
        print("\n❌ Failed to initialize database")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\nTroubleshooting tips:")
        print(
            "1. Make sure Docker is running with: docker compose -f docker/compose.yml up -d db"
        )
        print("2. Check the database container is healthy with: docker ps")
        print(
            "3. Try manually connecting to the database: docker exec -it docker-db-1 psql -U postgres"
        )
        sys.exit(1)
    else:
        print("\nYou can now start the API server with: python run.py")
