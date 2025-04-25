import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship # Import relationship even if not used immediately

from app.core.db import Base # Import Base from the correct location

class User(Base):
    __tablename__ = "users"

    # Using Integer for simplicity, could be UUID if preferred later
    id = Column(Integer, primary_key=True, index=True)
    # If using UUIDs:
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    # hashed_password = Column(String, nullable=False) # Removed hashed_password column
    is_active = Column(Boolean(), default=True)
    # is_superuser = Column(Boolean(), default=False) # Optional: Add if needed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationships here if needed in the future, e.g.:
    # projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"