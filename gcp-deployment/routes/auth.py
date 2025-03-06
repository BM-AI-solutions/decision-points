from flask import Blueprint, request, jsonify
import uuid
import jwt
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from google.auth.transport import requests
from google.oauth2 import id_token

from utils.logger import setup_logger

bp = Blueprint('auth', __name__)
logger = setup_logger('routes.auth')

# Mock user database for demonstration
USERS = {}

@bp.route('/register', methods=['POST'])
def register():
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

        if email in USERS:
            return jsonify({
                'error': 'Email already registered',
                'status': 409
            }), 409

        user_id = str(uuid.uuid4())

        # In a real application, you would store this in a database
        USERS[email] = {
            'id': user_id,
            'email': email,
            'password_hash': generate_password_hash(password),
            'name': name,
            'created_at': datetime.utcnow().isoformat(),
            'credits': 10,  # Give new users some starter credits
            'subscription': None
        }

        logger.info(f"Registered new user: {email}")
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

        if email not in USERS:
            return jsonify({
                'error': 'Invalid email or password',
                'status': 401
            }), 401

        user = USERS[email]

        if not check_password_hash(user['password_hash'], password):
            return jsonify({
                'error': 'Invalid email or password',
                'status': 401
            }), 401

        # Generate JWT token
        secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
        expiration = datetime.utcnow() + timedelta(hours=24)

        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': expiration
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')

        logger.info(f"User login: {email}")
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'credits': user['credits']
            }
        })

    except Exception as e:
        logger.error(f"Error logging in: {str(e)}", exc_info=True)
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

        # Find user
        user = None
        for u in USERS.values():
            if u['id'] == user_id:
                user = u
                break

        if not user:
            return jsonify({
                'error': 'User not found',
                'status': 404
            }), 404

        logger.info(f"Retrieved profile for user: {email}")
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'credits': user['credits'],
                'subscription': user['subscription']
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
            google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '116937668968-g0d3oevk2uh6ikng4igu18l4jjq6puhs.apps.googleusercontent.com')
            
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

            # Check if user exists, if not create one
            user = None
            if email in USERS:
                user = USERS[email]
                # Update user's Google ID if not already set
                if not user.get('google_id'):
                    user['google_id'] = google_id
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                user = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'google_id': google_id,
                    'created_at': datetime.utcnow().isoformat(),
                    'credits': 10,  # Give new users some starter credits
                    'subscription': None
                }
                USERS[email] = user

            # Generate JWT token
            secret_key = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
            expiration = datetime.utcnow() + timedelta(hours=24)

            payload = {
                'user_id': user['id'],
                'email': user['email'],
                'exp': expiration
            }

            token = jwt.encode(payload, secret_key, algorithm='HS256')

            logger.info(f"User logged in with Google: {email}")
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'credits': user.get('credits', 10)
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

        # Find user
        if email not in USERS:
            return jsonify({
                'error': 'User not found',
                'status': 404
            }), 404

        user = USERS[email]

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

        # In a real application, you would process the payment
        # For this demonstration, we'll just update the user's credits

        package = packages[package_id]
        user['credits'] += package['credits']

        logger.info(f"User {email} purchased {package['credits']} credits")
        return jsonify({
            'success': True,
            'credits': user['credits'],
            'transaction': {
                'id': str(uuid.uuid4()),
                'package_id': package_id,
                'credits': package['credits'],
                'price': package['price'],
                'date': datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error purchasing credits: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error purchasing credits',
            'message': str(e),
            'status': 500
        }), 500
