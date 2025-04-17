import os
import jwt
from functools import wraps
from flask import request, jsonify, current_app

from config import Config
from models.user import UserProfile # Assuming UserProfile model is accessible

# Import necessary components for user fetching and subscription check
if Config.BILLING_REQUIRED:
    try:
        from google.cloud import datastore
        datastore_client = datastore.Client()
    except ImportError:
        current_app.logger.error("google-cloud-datastore not installed, but BILLING_REQUIRED is True.")
        datastore_client = None # Handle gracefully if import fails
    # In-memory stores are not needed when billing is required
    USERS = {}
    USER_IDS = {}
else:
    # Import in-memory stores if not using Datastore
    # This assumes auth.py defines these globally or they are accessible.
    # If they are instance variables, this approach needs rethinking.
    # A better approach might be to pass a user lookup function to the decorator.
    try:
        # Corrected import path (relative to /app inside container)
        from routes.auth import USERS, USER_IDS
    except ImportError:
         # Commented out: This runs at import time, before app context exists
         # current_app.logger.warning("Could not import USERS/USER_IDS from auth.py for local mode.")
         # Fallback if import fails (e.g., circular import)
         USERS = {}
         USER_IDS = {}
    datastore_client = None # Ensure datastore_client is None in local mode
    datastore = None # Ensure datastore is None in local mode


# --- Subscription Check Helper ---
def has_active_subscription(user_profile_or_entity):
    """
    Check if the user has an active subscription.
    Handles both UserProfile objects and Datastore entities.
    """
    if not Config.BILLING_REQUIRED:
        return True # Always true in local mode

    subscription_data = None
    if Config.BILLING_REQUIRED and datastore and isinstance(user_profile_or_entity, datastore.Entity):
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
def require_subscription_or_local(f):
    """
    Decorator to restrict access to routes based on BILLING_REQUIRED flag
    and user subscription status (if billing is required).
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        logger = current_app.logger # Use Flask's app logger

        # 1. Check JWT Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Authorization header missing or invalid.")
            return jsonify({'error': 'Authorization required', 'status': 401}), 401

        token = auth_header.split(' ')[1]
        # Use Config default as fallback if env var not explicitly set
        secret_key = os.environ.get('JWT_SECRET_KEY', Config.JWT_SECRET_KEY)

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            # email = payload.get('email') # Email might not always be in payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"JWT token expired.")
            return jsonify({'error': 'Token expired', 'status': 401}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return jsonify({'error': 'Invalid token', 'status': 401}), 401
        except KeyError:
             logger.warning(f"user_id missing from JWT payload.")
             return jsonify({'error': 'Invalid token payload', 'status': 401}), 401

        # 2. Fetch User Profile/Entity
        user_data = None
        if Config.BILLING_REQUIRED:
            if not datastore_client:
                 logger.error("Datastore client not initialized despite BILLING_REQUIRED being True.")
                 return jsonify({'error': 'Server configuration error', 'status': 500}), 500
            try:
                key = datastore_client.key('User', user_id)
                user_data = datastore_client.get(key) # Fetch the entity
                if not user_data:
                     logger.warning(f"User profile not found in Datastore for user_id: {user_id}")
                     return jsonify({'error': 'User profile not found', 'status': 404}), 404
            except Exception as e:
                 logger.error(f"Error fetching user profile from Datastore for user_id {user_id}: {e}", exc_info=True)
                 return jsonify({'error': 'Error fetching user profile', 'status': 500}), 500
        else:
            # Local mode: Fetch from in-memory store
            local_email = USER_IDS.get(user_id)
            if local_email and local_email in USERS:
                 profile_dict = USERS[local_email]
                 # Create a simple object that behaves like UserProfile for has_active_subscription
                 user_data = type('UserProfileMock', (), profile_dict)()
                 # Ensure necessary attributes exist, even if None
                 setattr(user_data, 'subscription', profile_dict.get('subscription'))

            if not user_data:
                logger.warning(f"User profile not found in local store for user_id: {user_id}")
                return jsonify({'error': 'User profile not found', 'status': 404}), 404

        # 3. Check Subscription if Billing Required
        if Config.BILLING_REQUIRED:
            if not has_active_subscription(user_data):
                logger.warning(f"Access denied for user {user_id}: No active subscription.")
                return jsonify({'error': 'Active subscription required for this feature', 'status': 403}), 403
            else:
                 logger.debug(f"Subscription check passed for user {user_id}.")
        else:
             logger.debug(f"Billing not required, access granted for user {user_id}.")

        # Pass user_id to the decorated function via kwargs
        kwargs['user_id'] = user_id
        # Optionally pass user_data if needed: kwargs['user_data'] = user_data

        return await f(*args, **kwargs)
    return decorated_function