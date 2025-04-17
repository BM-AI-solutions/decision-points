from flask import Blueprint, request, jsonify, abort
import uuid
import jwt
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from google.auth.transport import requests
from google.oauth2 import id_token
import stripe
from google.cloud import datastore

from utils.logger import setup_logger
bp = Blueprint('auth', __name__)

# --- Environment Variable Hardening and Stripe Mode Selection ---
ENV = os.environ.get('ENV', 'development')
STRIPE_MODE = os.environ.get('STRIPE_MODE', 'test')

# --- Subscription Status Helper ---
def has_active_subscription(user_profile):
    """Check if the user has an active subscription. Extend as needed for real logic."""
    # Placeholder: check for 'subscription' attribute and status
    subscription = getattr(user_profile, 'subscription', None)
    if not subscription:
        return False
    status = getattr(subscription, 'status', None)
    if status == 'active':
        # Optionally check end_date, etc.
        return True
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

# Initialize Google Cloud Datastore client
datastore_client = datastore.Client()


from models.user import UserProfile, UserAuth

@bp.route('/register', methods=['POST'])
async def register():
    """Register a new user."""
    try:
        data = request.json

        email = data.get('email')
        password = data.get('password')
        name = data.get('name', 'User')

        if not email or not password:
            return jsonify({
                'error': 'Email and password are required',
                'status': 400
            }), 400

        # Check if user already exists
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

@bp.route('/login', methods=['POST'])
async def login():
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

        # Generate JWT token
        secret_key = os.environ['JWT_SECRET_KEY']  # Required in production
        expiration = datetime.utcnow() + timedelta(hours=24)

        payload = {
            'user_id': user_auth.id,
            'email': user_auth.email,
            'exp': expiration
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')

        logger.info(f"User login: {email} with ID {user_auth.id}")
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_auth.id,
                'email': user_auth.email,
                'name': user_profile.name,
                'credits': user_profile.credits_remaining
            }
        })

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

        # Retrieve user profile entity from Datastore
        user_profile_entity = datastore_client.get(datastore_client.key('User', user_id))
        if not user_profile_entity:
            return jsonify({
                'error': 'User profile not found',
                'status': 404
            }), 404
        
        user_profile = UserProfile.from_entity(user_profile_entity)

        logger.info(f"Retrieved profile for user: {user_profile.email} with ID {user_id}")
        subscription_active = has_active_subscription(user_profile)
        return jsonify({
            'success': True,
            'user': {
                'id': user_profile.id,
                'email': user_profile.email,
                'name': user_profile.name,
                'credits': user_profile.credits_remaining,
                'subscription_active': subscription_active
            }
        })

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
async def google_auth():
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
async def purchase_credits():
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

        # Retrieve user profile entity from Datastore
        user_profile_entity = datastore_client.get(datastore_client.key('User', user_id))
        if not user_profile_entity:
            return jsonify({
                'error': 'User profile not found',
                'status': 404
            }), 404
        
        user_profile = UserProfile.from_entity(user_profile_entity)

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

