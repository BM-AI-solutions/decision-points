import os
from typing import Dict, Any

class Config:
    """Application configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

    # API Keys
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    # Database settings (if using a database)
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'decision-points.log')

    # Security settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400 * 30))  # 30 days
    
    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')

    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per day, 10 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

    # Agent settings
    GUIDE_AGENT_MODEL = os.environ.get('GUIDE_AGENT_MODEL', 'gpt-4o')
    ACTION_AGENT_MODEL = os.environ.get('ACTION_AGENT_MODEL', 'gpt-4o')

    # Payment settings (if implementing subscriptions)
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # Feature flags
    FEATURES = {
        'subscriptions': os.environ.get('FEATURE_SUBSCRIPTIONS', 'false').lower() == 'true',
        'credits': os.environ.get('FEATURE_CREDITS', 'false').lower() == 'true',
        'branding_generator': os.environ.get('FEATURE_BRANDING_GENERATOR', 'true').lower() == 'true',
        'revenue_sharing': os.environ.get('FEATURE_REVENUE_SHARING', 'false').lower() == 'true',
    }

    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """Get all configured API keys."""
        return {
            'google': cls.GOOGLE_API_KEY,
            'stripe': cls.STRIPE_API_KEY,
        }
