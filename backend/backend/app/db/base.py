# Import all the models for SQLAlchemy to discover them
from app.db.base_class import Base
from app.models.user import User, UserRole
from app.models.assignment import Assignment, StudentAssignment
