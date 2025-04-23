import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete # Avoid name collision
from typing import List, Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash # Will be created later

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users with pagination."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    """Create a new user."""
    try:
        # Hash the password before storing
        hashed_password = get_password_hash(user_in.password) # Use the utility function
        db_user = User(
            email=user_in.email,
            name=user_in.name,
            hashed_password=hashed_password,
            # is_active defaults to True in the model
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"User created successfully: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        await db.rollback() # Rollback the transaction in case of error
        raise # Re-raise the exception to be handled by the API endpoint

async def update_user(db: AsyncSession, *, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user."""
    update_data = user_in.dict(exclude_unset=True) # Pydantic V1

    # If password is being updated, hash it
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"] # Remove plain password from update dict
    elif "password" in update_data:
         del update_data["password"] # Remove if it's None or empty

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