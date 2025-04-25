from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete # Avoid name collision
from typing import List, Optional

from app.models.user import User
from app.schemas.user import UserUpdate # Removed UserCreate
# from app.core.security import get_password_hash # Removed password hashing dependency

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users with pagination."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def update_user(db: AsyncSession, *, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user."""
    update_data = user_in.dict(exclude_unset=True) # Pydantic V1

    # Remove password update logic as authentication is removed
    if "password" in update_data:
        del update_data["password"]
    if "hashed_password" in update_data: # Also remove direct hashed_password updates if schema allows
        del update_data["hashed_password"]


    if update_data: # Only proceed if there's something to update
        # Use SQLAlchemy Core update statement for efficiency with async
        stmt = (
            sqlalchemy_update(User)
            .where(User.id == db_user.id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch") # Or False, depending on strategy
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(db_user) # Refresh the instance to get updated values

    return db_user


async def delete_user(db: AsyncSession, *, user_id: int) -> Optional[User]:
    """Delete a user by ID."""
    # Retrieve the user first to return it (optional, could just return success/fail)
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        return None

    # Use SQLAlchemy Core delete statement
    stmt = sqlalchemy_delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    # The db_user object is now detached and represents the state before deletion
    return db_user

# You might want to group these functions into a class-based CRUD utility later
# class CRUDUser:
#     async def get(...)
#     async def get_by_email(...)
#     ...
# user = CRUDUser()