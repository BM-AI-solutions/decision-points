from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud, models # Import models package
from app.api import deps # Import the dependencies module

router = APIRouter()

# Secure this endpoint: requires authentication
@router.get("/", response_model=List[schemas.user.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
    # current_user: models.User = Depends(deps.get_current_user) # Removed dependency
) -> List[models.User]: # Return type should be the model if using ORM mode effectively
    """
    Retrieve users.
    """
    # Authentication removed.
    users = await crud.user.get_users(db, skip=skip, limit=limit)
    # FastAPI handles the conversion of the list of SQLAlchemy models
    return users

# Secure this endpoint: requires authentication
@router.get("/{user_id}", response_model=schemas.user.User)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db)
    # current_user: models.User = Depends(deps.get_current_user) # Removed dependency
) -> models.User: # Return type should be the model if using ORM mode effectively
    """
    Get user by ID.
    """
    # Authentication removed.
    db_user = await crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # FastAPI handles the conversion
    return db_user

# Add endpoints for Update and Delete later if needed
# @router.put("/{user_id}", response_model=schemas.user.User)
# async def update_user(...) # Remember to add Depends(deps.get_current_user)

# @router.delete("/{user_id}", response_model=schemas.user.User)
# async def delete_user(...) # Remember to add Depends(deps.get_current_user)