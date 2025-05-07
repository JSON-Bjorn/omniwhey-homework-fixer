from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with PRD templates created by this user
    templates = relationship(
        "Template", back_populates="creator", cascade="all, delete-orphan"
    )

    # Relationship with PRDs created by this user
    prds = relationship("PRD", back_populates="creator", cascade="all, delete-orphan")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    structure = Column(Text, nullable=False)  # JSON structure of the template
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with the user who created this template
    creator = relationship("User", back_populates="templates")

    # Relationship with PRDs created from this template
    prds = relationship("PRD", back_populates="template", cascade="all, delete-orphan")


class PRD(Base):
    __tablename__ = "prds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # JSON content based on template
    template_id = Column(Integer, ForeignKey("templates.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with the template used for this PRD
    template = relationship("Template", back_populates="prds")

    # Relationship with the user who created this PRD
    creator = relationship("User", back_populates="prds")

    # Relationship with collaborators
    collaborations = relationship(
        "Collaboration", back_populates="prd", cascade="all, delete-orphan"
    )


class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    prd_id = Column(Integer, ForeignKey("prds.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    permission = Column(String, default="read")  # read, write, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with the PRD
    prd = relationship("PRD", back_populates="collaborations")

    # Relationship with the user
    user = relationship("User")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, reviewed, rejected
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with the user who created this submission
    user = relationship("User")

    # Relationship with feedback
    feedback = relationship(
        "Feedback",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    grade = Column(String, nullable=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with the submission
    submission = relationship("Submission", back_populates="feedback")
