import os
import jwt
from functools import wraps
# Removed Flask imports: request, jsonify, current_app
from typing import Optional # Added for type hinting

from config import Config
# from models.user import UserProfile # Assuming UserProfile model is accessible - Check if needed
from routes import auth # Import the auth module

# Import necessary components for user fetching and subscription check
if Config.BILLING_REQUIRED:
    try:
        from google.cloud import datastore
        datastore_client = datastore.Client()
        # Define datastore for type hinting consistency if needed elsewhere
        # datastore = google.cloud.datastore # Example
    except ImportError:
        # This will likely crash the app if datastore is needed, which is intended.
        # Log the error during app initialization instead.
        print("ERROR: google-cloud-datastore not installed, but BILLING_REQUIRED is True.")
        datastore_client = None
    # datastore = None # Define datastore for consistency, even if client fails
else:
    # In local mode, we will access USERS and USER_IDS via the imported auth module
    datastore_client = None
    # datastore = None

# Import logger
from utils.logger import setup_logger
logger = setup_logger('utils.decorators')

# --- Subscription Check Helper ---
def has_active_subscription(user_profile_or_entity):
    """
    Check if the user has an active subscription.
    Handles both UserProfile objects and Datastore entities.
    """
    if not Config.BILLING_REQUIRED:
        return True # Always true in local mode

    subscription_data = None
    # Check if datastore_client is initialized and the entity type matches
    if Config.BILLING_REQUIRED and datastore_client and type(user_profile_or_entity).__name__ == 'Entity': # Basic check for Datastore entity
        # It's a Datastore entity
        subscription_data = user_profile_or_entity.get('subscription', None)
    elif hasattr(user_profile_or_entity, 'subscription'):
         # It's likely a UserProfile object (or mock)
         subscription_data = getattr(user_profile_or_entity, 'subscription', None)

    if not subscription_data:
        return False # No subscription data found

    # Check status within the subscription data (could be dict or object)
    status = None
    if isinstance(subscription_data, dict):
        status = subscription_data.get('status')
    elif hasattr(subscription_data, 'status'):
        status = getattr(subscription_data, 'status', None)

    if status == 'active':
        # Optionally check end_date, etc.
        return True

    return False

# --- Access Control Decorator ---

# TODO: Reimplement require_subscription_or_local as a FastAPI dependency.
# This dependency should:
# 1. Depend on a JWT verification dependency (like `get_current_user` from security_enhancements.py)
#    to get the authenticated user's ID.
# 2. Fetch the user's profile/data based on the user ID.
#    - If Config.BILLING_REQUIRED is True, use the `datastore_client` (or an injected service).
#    - If Config.BILLING_REQUIRED is False, use the local `auth.USERS` / `auth.USER_IDS`.
#    - Handle cases where the user profile is not found (raise HTTPException 404).
#    - Handle potential errors during data fetching (raise HTTPException 500).
# 3. If Config.BILLING_REQUIRED is True, call `has_active_subscription(user_data)`.
#    - If the check fails, raise HTTPException 403 (Forbidden).
# 4. If all checks pass, the dependency can simply complete (implicitly granting access)
#    or return the user_id or user_data if needed by the path operation function.
# 5. Use the standard `logger` for logging messages.
# 6. Use `raise HTTPException` from `fastapi` for errors instead of `jsonify`.

# Example Usage in FastAPI path operation:
# from fastapi import Depends
#
# @app.get("/some/protected/route", dependencies=[Depends(verify_subscription_or_local)])
# async def protected_route():
#     # Access granted if dependency runs without raising exception
#     # User ID can be obtained from the JWT dependency if needed separately
#     return {"message": "Access granted to protected route"}
#
# async def verify_subscription_or_local(current_user: dict = Depends(get_current_user)): # Assuming get_current_user provides {'user_id': ...}
#     user_id = current_user['user_id']
#     logger.debug(f"Checking subscription/local access for user_id: {user_id}")
#
#     # ... [Implement steps 2-5 as described above] ...
#
#     # Example check:
#     user_data = fetch_user_data(user_id) # Replace with actual fetching logic
#     if Config.BILLING_REQUIRED and not has_active_subscription(user_data):
#         logger.warning(f"Access denied for user {user_id}: No active subscription.")
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active subscription required")
#
#     logger.debug(f"Access check passed for user {user_id}.")
#     # Optionally return user_data if needed by the endpoint
#     # return user_data