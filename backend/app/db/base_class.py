from typing import Any, Dict, TypeVar, Generic, Type
import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for SQLAlchemy models.

    Note: The 'id' field is not defined here anymore as it will be defined
    in the derived classes to allow for different primary key types.
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
