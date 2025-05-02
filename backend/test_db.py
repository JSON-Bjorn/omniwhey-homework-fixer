import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.models import User, Token, Submission


def test_db_connection():
    try:
        # Test if we can connect to the database
        connection = engine.connect()
        connection.close()
        print("Successfully connected to the database!")
        return True
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False


def test_user_query():
    db = SessionLocal()
    try:
        # Test if we can query users
        users = db.query(User).all()
        print(f"Found {len(users)} users in the database.")
        for user in users:
            print(f"User: {user.email}, Active: {user.is_active}")
        return True
    except Exception as e:
        print(f"Error querying users: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Testing database connection...")
    if test_db_connection():
        print("Testing user queries...")
        test_user_query()
    else:
        print("Failed to connect to the database. Check your configuration.")
