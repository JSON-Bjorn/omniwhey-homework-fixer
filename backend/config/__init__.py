"""
Configuration package for the OmniWhey API
"""

# Import database configurations using relative import
from .database import SessionLocal, engine, Base, get_db

# Export these to be available from config package
__all__ = ["SessionLocal", "engine", "Base", "get_db"]
