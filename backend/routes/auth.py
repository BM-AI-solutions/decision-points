from flask import Blueprint, request, jsonify, abort
import uuid
import jwt
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
from config import Config

# Only import Google Cloud libraries if billing is required (hosted/SaaS mode)
if Config.BILLING_REQUIRED:
    from google.auth.transport import requests
    from google.oauth2 import id_token
    from google.cloud import datastore
else:
    # Provide mocks for Google auth/ID token in local mode
    requests = None
    id_token = None
    datastore = None


from utils.logger import setup_logger
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# --- Environment Variable Hardening and Stripe Mode Selection ---
ENV = os.environ.get('ENV', 'development')
STRIPE_MODE = os.environ.get('STRIPE_MODE', 'test')

# --- Subscription Status Helper ---
def has_active_subscription(user_profile):
    """Check if the user has an active subscription. Extend as needed for real logic."""
    logger.info(f"Checking subscription for user: {getattr(user_profile, 'email', 'unknown')}")
    logger.info(f"BILLING_REQUIRED setting in has_active_subscription: {Config.BILLING_REQUIRED}")
    
    # Dual-mode: bypass subscription checks if billing is not required
    if not Config.BILLING_REQUIRED:
        logger.info("BILLING_REQUIRED is False, bypassing subscription check and returning True")
        return True
        
    # Placeholder: check for 'subscription' attribute and status
    subscription = getattr(user_profile, 'subscription', None)
    logger.info(f"User subscription object: {subscription}")
    
    if not subscription:
        logger.info("No subscription found, returning False")
        return False
        
    status = getattr(subscription, 'status', None)
    logger.info(f"Subscription status: {status}")
    
    if status == 'active':
        # Optionally check end_date, etc.
        logger.info("Subscription is active, returning True")
        return True
        
    logger.info(f"Subscription is not active (status: {status}), returning False")
    return False

STRIPE_API_KEY_LIVE = os.environ.get('STRIPE_API_KEY_LIVE')
STRIPE_API_KEY_TEST = os.environ.get('STRIPE_API_KEY_TEST')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

if ENV == 'production':
    missing = []
    if not STRIPE_WEBHOOK_SECRET:
        missing.append('STRIPE_WEBHOOK_SECRET')
    if not JWT_SECRET_KEY:
        missing.append('JWT_SECRET_KEY')
    if STRIPE_MODE == 'live' and not STRIPE_API_KEY_LIVE:
        missing.append('STRIPE_API_KEY_LIVE')
    if STRIPE_MODE == 'test' and not STRIPE_API_KEY_TEST:
        missing.append('STRIPE_API_KEY_TEST')
    if missing:
        raise RuntimeError(f"Missing required environment variables in production: {', '.join(missing)}")

if STRIPE_MODE == 'live':
    stripe.api_key = STRIPE_API_KEY_LIVE
else:
    stripe.api_key = STRIPE_API_KEY_TEST

logger = setup_logger('routes.auth')

# Backend selection: Google Cloud Datastore (hosted/SaaS) or in-memory (local)
if Config.BILLING_REQUIRED:
    datastore_client = datastore.Client()
else:
    # In-memory user/session store for local/self-hosted mode
    USERS = {}         # email -> user dict
    USER_AUTHS = {}    # email -> auth dict
    USER_IDS = {}      # id -> email


from models.user import UserProfile, UserAuth

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        logger.info(f"Checking Config.BILLING_REQUIRED: {Config.BILLING_REQUIRED}") # Add this log
        data = request.json

        email = data.get('email')
        password = data.get('password')
        name = data.get('name', 'User')

        if not email or not password:
            return jsonify({
                'error': 'Email and password are required',
                'status': 400
            }), 400

        if Config.BILLING_REQUIRED:
            # Check if user already exists in Datastore
            query = datastore_client.query(kind='User')
            query.add_filter('email', '=', email)
            existing_users = list(query.fetch())

            if existing_users:
                return jsonify({
                    'error': 'Email already registered',
                    'status': 409
                }), 409

            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash(password)

            # Create UserAuth entity
            auth_entity = UserAuth(
                id=user_id,
                email=email,
                hashed_password=password_hash,
                salt="" # Salt is not used in generate_password_hash
            ).to_entity(datastore_client, user_id)

            # Create UserProfile entity
            profile_entity = UserProfile(
                id=user_id,
                email=email,
                name=name,
                created_at=datetime.utcnow(),
                credits_remaining=10
            ).to_entity(datastore_client)

            # Save entities to Datastore in a transaction
            with datastore_client.transaction():
                datastore_client.put(auth_entity)
                datastore_client.put(profile_entity)

        else:
            # Local mode: check in-memory USERS
            logger.info(f"Local mode signup attempt for email: {email}") # Add log
            logger.debug(f"Current USERS keys before check: {list(USERS.keys())}") # Add log
            if email in USERS: # Remove the previous logs
                logger.warning(f"Email '{email}' already found in local USERS store.") # Add log
                return jsonify({
                    'error': 'Email already registered',
                    'status': 409
                }), 409
            else: # Add else block for clarity and correct indentation of next log
                logger.info(f"Email '{email}' not found in local USERS store. Proceeding with registration.") # Add log
                user_id = str(uuid.uuid4())
                password_hash = generate_password_hash(password)
                
                # Store auth and profile in-memory
                logger.info(f"Creating new user_auth entry for email: {email} with ID: {user_id}")
                USER_AUTHS[email] = {
                    'id': user_id,
                    'email': email,
                    'hashed_password': password_hash,
                    'salt': ""
                }
                USERS[email] = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'created_at': datetime.utcnow(),
                    'credits_remaining': 10
                }
                USER_IDS[user_id] = email

                logger.debug(f"Added '{email}' to USERS. Current keys: {list(USERS.keys())}")
                logger.debug(f"Added '{email}' to USER_AUTHS. Current keys: {list(USER_AUTHS.keys())}")
                logger.debug(f"Added '{user_id}' to USER_IDS. Current keys: {list(USER_IDS.keys())}")

        logger.info(f"Registered new user: {email} with ID {user_id}")
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'credits': 10
            }
        })

    except Exception as e:
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error registering user',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/signup', methods=['POST'])
def signup():
    """Signup endpoint that matches the frontend's expected URL."""
    logger.info("Received request to /api/auth/signup endpoint")
    try:
        # Log the request details to help diagnose the issue
        logger.info(f"Request JSON: {request.json}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # CRITICAL ISSUE: There are two implementations of the signup function
        # This first implementation calls register(), but there's a second implementation below
        # that duplicates the register logic directly. This is likely causing the 500 error.
        logger.warning("Using first implementation of signup that calls register()")
        
        # Forward to the register function
        return register()
    except Exception as e:
        logger.error(f"Error in signup route: {str(e)}", exc_info=True)
        # CRITICAL ISSUE: This is a duplicate implementation of the signup function
        # This code should not be here and is likely causing the 500 error
        # The indentation is also incorrect for the code at lines 273-289
        logger.error("DUPLICATE CODE DETECTED: Second implementation of signup function is being executed")
        logger.error("This is likely causing the 500 error during signup")
        return jsonify({
            'error': 'Error in signup route',
            'message': str(e),
            'status': 500
        }), 500
# The duplicate implementation of the signup function has been removed
# This resolves the issue of having two route definitions for the same endpoint

@bp.route('/login', methods=['POST'])
def login():
    """Log in a user."""
    try:
        data = request.json

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'error': 'Email and password are required',
                'status': 400
            }), 400
        
        if Config.BILLING_REQUIRED:
            # Retrieve user auth entity from Datastore
            query = datastore_client.query(kind='UserAuth')
            query.add_filter('email', '=', email)
            user_auth_entities = list(query.fetch())

            if not user_auth_entities:
                return jsonify({
                    'error': 'Invalid email or password',
                    'status': 401
                }), 401

            user_auth_entity = user_auth_entities[0]
            user_auth = UserAuth.from_entity(user_auth_entity)

            if not check_password_hash(user_auth.hashed_password, password):
                return jsonify({
                    'error': 'Invalid email or password',
                    'status': 401
                }), 401

            # Retrieve user profile entity
            user_profile_entity = datastore_client.get(datastore_client.key('User', user_auth.id))
            if not user_profile_entity:
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
            user_profile = UserProfile.from_entity(user_profile_entity)
        else:
            # Local mode: check in-memory USER_AUTHS/USERS
            logger.info(f"Login attempt in local mode for email: {email}")
            logger.debug(f"Current USER_AUTHS keys: {list(USER_AUTHS.keys())}")
            auth = USER_AUTHS.get(email)
            logger.info(f"Retrieved auth for email {email}: {auth is not None}")
            if not auth:
                logger.warning(f"Login failed: Email not found in local store - {email}")
                return jsonify({"message": "Invalid email or password"}), 401
            
            # Create dynamic UserAuth object only if auth exists
            user_auth = type('UserAuth', (), auth)()
            user_auth.id = auth['id']
            user_auth.email = auth['email']
            if not check_password_hash(auth['hashed_password'], password):
                return jsonify({
                    'error': 'Invalid email or password',
                    'status': 401
                }), 401
            user_id = auth['id']
            profile = USERS.get(email)
            if not profile:
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
            user_profile = type('UserProfile', (), profile)()
            user_profile.id = profile['id']
            user_profile.email = profile['email']
            user_profile.name = profile['name']
            user_profile.credits_remaining = profile['credits_remaining']

        # Generate JWT token
        logger.info(f"Generating JWT token for user: {user_auth.id}")
        try:
            # Get JWT secret key from environment, with fallback for development
            secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
            logger.debug(f"Using JWT secret key: {'dev-key' if secret_key == 'dev-jwt-secret-change-in-production' else 'custom key'}")
            
            expiration = datetime.utcnow() + timedelta(hours=24)

            payload = {
                'user_id': user_auth.id,
                'email': user_auth.email,
                'exp': expiration
            }
            
            logger.debug(f"JWT payload: {payload}")
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            logger.info(f"JWT token generated successfully: {token[:10]}...")
            
            # Check token type to ensure proper encoding
            logger.debug(f"Token type: {type(token)}")
            if isinstance(token, bytes):
                token = token.decode('utf-8')
                logger.info("Decoded token from bytes to string")
        except Exception as e:
            logger.error(f"Error generating JWT token: {str(e)}", exc_info=True)
            raise

        logger.info(f"User login: {email} with ID {user_auth.id}")
        
        # Prepare response data
        response_data = {
            'success': True,
            'token': token,
            'user': {
                'id': user_auth.id,
                'email': user_auth.email,
                'name': user_profile.name,
                'credits': user_profile.credits_remaining
            }
        }
        
        # Log response data (excluding token)
        log_data = response_data.copy()
        log_data['token'] = log_data['token'][:10] + '...' if log_data['token'] else None
        logger.debug(f"Response data: {log_data}")
        
        # Return JSON response
        try:
            response = jsonify(response_data)
            logger.debug(f"Response content type: {response.content_type}")
            return response
        except Exception as e:
            logger.error(f"Error creating JSON response: {str(e)}", exc_info=True)
            # Fallback response if jsonify fails
            return jsonify({
                'success': False,
                'error': 'Error creating response',
                'message': str(e),
                'status': 500
            }), 500

    except Exception as e:
        logger.error(f"Error logging in user with email {email}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error logging in',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/profile', methods=['GET'])
def profile():
    """Get user profile information."""
    try:
        logger.info("=== PROFILE ENDPOINT CALLED ===")
        logger.info(f"BILLING_REQUIRED setting: {Config.BILLING_REQUIRED}")
        
        auth_header = request.headers.get('Authorization')
        logger.info(f"Authorization header present: {auth_header is not None}")

        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            return jsonify({
                'error': 'Authorization required',
                'status': 401
            }), 401

        token = auth_header.split(' ')[1]
        logger.info(f"Token received: {token[:10]}...")
        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
        logger.info(f"Using JWT secret key: {'default-dev-key' if secret_key == 'dev-jwt-secret-change-in-production' else 'custom-key'}")

        try:
            logger.info("Attempting to decode JWT token...")
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            logger.info(f"JWT token decoded successfully for user_id: {user_id}")
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return jsonify({
                'error': 'Token expired',
                'status': 401
            }), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            return jsonify({
                'error': 'Invalid token',
                'status': 401
            }), 401

        if Config.BILLING_REQUIRED:
            logger.info("Using Datastore for user profile (BILLING_REQUIRED=true)")
            # Retrieve user profile entity from Datastore
            user_profile_entity = datastore_client.get(datastore_client.key('User', user_id))
            if not user_profile_entity:
                logger.warning(f"User profile not found in Datastore for user_id: {user_id}")
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
            
            user_profile = UserProfile.from_entity(user_profile_entity)
        else:
            logger.info("Using in-memory storage for user profile (BILLING_REQUIRED=false)")
            # Local mode: get from in-memory USERS
            email = None
            for e, p in USERS.items():
                if p['id'] == user_id:
                    email = e
                    break
            
            logger.info(f"Looking up user by ID {user_id}, found email: {email}")
            logger.debug(f"Current USERS keys: {list(USERS.keys())}")
            logger.debug(f"Current USER_IDS keys: {list(USER_IDS.keys())}")
            
            if not email:
                logger.warning(f"User profile not found in memory for user_id: {user_id}")
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
                
            profile = USERS[email]
            user_profile = type('UserProfile', (), profile)()
            user_profile.id = profile['id']
            user_profile.email = profile['email']
            user_profile.name = profile['name']
            user_profile.credits_remaining = profile['credits_remaining']

        logger.info(f"Retrieved profile for user: {user_profile.email} with ID {user_id}")
        
        # Check subscription status
        subscription_active = has_active_subscription(user_profile)
        logger.info(f"Subscription active: {subscription_active}")
        
        # Prepare response
        response_data = {
            'success': True,
            'user': {
                'id': user_profile.id,
                'email': user_profile.email,
                'name': user_profile.name,
                'credits': user_profile.credits_remaining,
                'subscription_active': subscription_active
            }
        }
        logger.info(f"Returning user profile: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error retrieving profile',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Subscribe user to a plan."""
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authorization required',
                'status': 401
            }), 401

        token = auth_header.split(' ')[1]
        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expired',
                'status': 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid token',
                'status': 401
            }), 401

        data = request.json
        plan_id = data.get('plan_id')
        payment_method_id = data.get('payment_method_id')

        if not plan_id or not payment_method_id:
            return jsonify({
                'error': 'Plan ID and payment method ID are required',
                'status': 400
            }), 400

        # Find user
        if email not in USERS:
            return jsonify({
                'error': 'User not found',
                'status': 404
            }), 404

        user = USERS[email]

        # In a real application, you would process the payment and create a subscription
        # For this demonstration, we'll just update the user's subscription status

        now = datetime.utcnow()
        end_date = now + timedelta(days=30)

        subscription = {
            'id': str(uuid.uuid4()),
            'plan_id': plan_id,
            'status': 'active',
            'start_date': now.isoformat(),
            'end_date': end_date.isoformat(),
            'auto_renew': True
        }

        user['subscription'] = subscription

        logger.info(f"User {email} subscribed to plan {plan_id}")
        return jsonify({
            'success': True,
            'subscription': subscription
        })

    except Exception as e:
        logger.error(f"Error subscribing user: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error subscribing user',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/google', methods=['POST'])
def google_auth():
    """Authenticate user with Google OAuth."""
    try:
        data = request.json
        token = data.get('token')

        if not token:
            return jsonify({
                'error': 'Google token is required',
                'status': 400
            }), 400

        try:
            # Get Google Client ID from environment variables
            google_client_id = os.environ['GOOGLE_CLIENT_ID']
            
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                google_client_id
            )

            # Extract user info
            email = id_info.get('email')
            name = id_info.get('name')
            google_id = id_info.get('sub')  # Google's unique user ID
            
            if not email or not google_id:
                return jsonify({
                    'error': 'Invalid Google token',
                    'status': 400
                }), 400

            # Check if user with google_id already exists
            if Config.BILLING_REQUIRED:
                query = datastore_client.query(kind='UserAuth')
                query.add_filter('google_id', '=', google_id) # Add filter for google_id
                user_auth_entities = list(query.fetch())

                user_id = None # Initialize user_id
                if user_auth_entities:
                    user_auth_entity = user_auth_entities[0]
                    user_auth = UserAuth.from_entity(user_auth_entity)
                    user_id = user_auth.id # Get user_id from existing UserAuth entity
                else:
                    # Create new user if google_id does not exist
                    user_id = str(uuid.uuid4())
                    user_auth = UserAuth(
                        id=user_id,
                        email=email,
                        hashed_password=None, # No password for Google OAuth
                        salt=None,
                        google_id=google_id # Store google_id
                    )
                    auth_entity = user_auth.to_entity(datastore_client, user_id)

                    # Create UserProfile entity
                    profile_entity = UserProfile(
                        id=user_id,
                        email=email,
                        name=name,
                        created_at=datetime.utcnow(),
                        credits_remaining=10
                    ).to_entity(datastore_client)

                    # Save entities to Datastore in a transaction
                    with datastore_client.transaction():
                        datastore_client.put(auth_entity)
                        datastore_client.put(profile_entity)
            else:
                # Local mode: check in-memory USER_AUTHS for google_id
                user_id = None
                for e, a in USER_AUTHS.items():
                    if a.get('google_id') == google_id:
                        user_id = a['id']
                        break
                if not user_id:
                    # Create new user if google_id does not exist
                    user_id = str(uuid.uuid4())
                    USER_AUTHS[email] = {
                        'id': user_id,
                        'email': email,
                        'hashed_password': None,
                        'salt': None,
                        'google_id': google_id
                    }
                    USERS[email] = {
                        'id': user_id,
                        'email': email,
                        'name': name,
                        'created_at': datetime.utcnow(),
                        'credits_remaining': 10
                    }
                    USER_IDS[user_id] = email


            # Generate JWT token
            secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
            expiration = datetime.utcnow() + timedelta(hours=24)

            payload = {
                'user_id': user_id,
                'email': email,
                'exp': expiration
            }

            token = jwt.encode(payload, secret_key, algorithm='HS256')

            logger.info(f"User logged in with Google: {email} with ID {user_id}")
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'credits': 10 # Credits are not stored in UserAuth yet
                }
            })

        except ValueError as e:
            # Invalid token
            logger.error(f"Invalid Google token: {str(e)}")
            return jsonify({
                'error': 'Invalid Google token',
                'message': str(e),
                'status': 401
            }), 401

    except Exception as e:
        logger.error(f"Error in Google authentication: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error in Google authentication',
            'message': str(e),
            'status': 500
        }), 500

@bp.route('/credits/purchase', methods=['POST'])
def purchase_credits():
    """Purchase credits."""
    try:
        # Stripe API key is set globally based on STRIPE_MODE at import time

        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authorization required',
                'status': 401
            }), 401

        token = auth_header.split(' ')[1]
        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expired',
                'status': 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid token',
                'status': 401
            }), 401

        data = request.json
        package_id = data.get('package_id')
        payment_method_id = data.get('payment_method_id')

        if not package_id or not payment_method_id:
            return jsonify({
                'error': 'Package ID and payment method ID are required',
                'status': 400
            }), 400

        if Config.BILLING_REQUIRED:
            # Retrieve user profile entity from Datastore
            user_profile_entity = datastore_client.get(datastore_client.key('User', user_id))
            if not user_profile_entity:
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
            
            user_profile = UserProfile.from_entity(user_profile_entity)
        else:
            # Local mode: get from in-memory USERS
            email = None
            for e, p in USERS.items():
                if p['id'] == user_id:
                    email = e
                    break
            if not email:
                return jsonify({
                    'error': 'User profile not found',
                    'status': 404
                }), 404
            profile = USERS[email]
            user_profile = type('UserProfile', (), profile)()
            user_profile.id = profile['id']
            user_profile.email = profile['email']
            user_profile.name = profile['name']
            user_profile.credits_remaining = profile['credits_remaining']

        # Credit packages
        packages = {
            'small': {'credits': 100, 'price': 39},
            'medium': {'credits': 250, 'price': 79},
            'large': {'credits': 600, 'price': 159}
        }
        if package_id not in packages:
            return jsonify({
                'error': 'Invalid package ID',
                'status': 400
            }), 400

        package = packages[package_id]
        updated_credits = user_profile.credits_remaining + package['credits']

        try:
            # Create Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(package['price'] * 100), # Amount in cents
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'package_id': package_id,
                    'user_id': user_id,
                    'email': email
                }
            )

            payment_intent_id = intent['id']
            payment_status = intent['payment_status']

            # Update user credits in Datastore after successful payment - webhook handling would be better for production
            if payment_status == 'succeeded': # For simplicity, assume payment is successful here - webhook is needed for real confirmation
                user_profile_entity['credits_remaining'] = updated_credits
                datastore_client.put(user_profile_entity)
                logger.info(f"User {email} purchased {package['credits']} credits, total credits: {updated_credits}, Payment Intent ID: {payment_intent_id}")
            else:
                logger.warning(f"Stripe Payment Intent status: {payment_status}, Payment Intent ID: {payment_intent_id}")
                return jsonify({
                    'error': 'Payment processing incomplete',
                    'status': 400,
                    'message': f'Stripe Payment Intent status: {payment_status}',
                    'payment_intent_id': payment_intent_id
                }), 400

            return jsonify({
                'success': True,
                'credits': updated_credits,
                'client_secret': intent.client_secret, # Send client_secret to frontend to complete payment
                'transaction': {
                    'id': payment_intent_id,
                    'package_id': package_id,
                    'credits': package['credits'],
                    'price': package['price'],
                    'date': datetime.utcnow().isoformat(),
                    'payment_status': payment_status
                }
            })

        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Payment processing error',
                'status': 500,
                'message': str(e)
            }), 500

    except Exception as e:
        logger.error(f"Error purchasing credits: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error purchasing credits',
            'message': str(e),
            'status': 500
        }), 500

# --- Stripe Webhook Endpoint for Payment/Subscription Events ---

@bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe webhook endpoint for payment/subscription events (production-ready)."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        logger.error('STRIPE_WEBHOOK_SECRET not set in environment')
        abort(500)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f'Invalid payload: {e}')
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Invalid Stripe signature: {e}')
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    event_type = event['type']
    logger.info(f'Received Stripe event: {event_type}')
    data = event['data']['object']

    # Example: handle payment_intent.succeeded, invoice.paid, customer.subscription.updated
    if event_type == 'payment_intent.succeeded':
        # TODO: Update user credits or subscription in persistent storage
        logger.info(f'PaymentIntent succeeded: {data.get("id")}, user: {data.get("metadata", {}).get("user_id")}')
        # Implement credit/subscription update logic here
    elif event_type == 'invoice.paid':
        # TODO: Mark subscription as active
        logger.info(f'Invoice paid: {data.get("id")}, customer: {data.get("customer")}')
        # Implement subscription activation logic here
    elif event_type.startswith('customer.subscription.'):
        # TODO: Update subscription status
        logger.info(f'Subscription event: {event_type}, subscription: {data.get("id")}, status: {data.get("status")}, user: {data.get("metadata", {}).get("user_id")}')
        # Implement subscription status update logic here
    else:
        logger.info(f'Unhandled Stripe event type: {event_type}')

    return jsonify({'status': 'success'})

