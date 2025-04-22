from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud, models # Import models package
from app.api import deps # Import the dependencies module

router = APIRouter()

# User creation remains unsecured for now as per instructions
@router.post("/", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
) -> models.User: # Return type should be the model if using ORM mode effectively
    """
    Create new user.
    """
    # Check if user already exists
    existing_user = await crud.user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    user = await crud.user.create_user(db=db, user_in=user_in)
    # FastAPI handles the conversion based on response_model and schema config (orm_mode/from_attributes)
    return user 

# Secure this endpoint: requires authentication
@router.get("/", response_model=List[schemas.user.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user) # Add dependency
) -> List[models.User]: # Return type should be the model if using ORM mode effectively
    """
    Retrieve users. Requires authentication.
    """
    # The current_user dependency ensures only authenticated users can access this.
    # We don't need to use the current_user object here yet, but it's available.
    users = await crud.user.get_users(db, skip=skip, limit=limit)
    # FastAPI handles the conversion of the list of SQLAlchemy models
    return users

# Secure this endpoint: requires authentication
@router.get("/{user_id}", response_model=schemas.user.User)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user) # Add dependency
) -> models.User: # Return type should be the model if using ORM mode effectively
    """
    Get user by ID. Requires authentication.
    """
    # The current_user dependency ensures only authenticated users can access this.
    # We could add checks here later, e.g., if current_user.id == user_id or if current_user is admin
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