"""
Analytics integration for production deployment.

This module provides:
1. User behavior tracking
2. Event tracking
3. Integration with analytics services (Google Analytics, Mixpanel, etc.)
4. Privacy-compliant data collection
"""

import os
import json
import time
import uuid
import hashlib
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps

# Removed Flask imports
from fastapi import Request # Added FastAPI Request

from utils.logger import setup_logger

# Set up module logger
logger = setup_logger('utils.analytics')

# ===== Analytics Configuration =====

class AnalyticsConfig:
    """Analytics configuration settings."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize analytics configuration."""
        self.config = config or {}

        # Google Analytics
        self.ga_enabled = self.config.get('ga_enabled', False)
        self.ga_measurement_id = self.config.get('ga_measurement_id')
        self.ga_api_secret = self.config.get('ga_api_secret')

        # Mixpanel
        self.mixpanel_enabled = self.config.get('mixpanel_enabled', False)
        self.mixpanel_token = self.config.get('mixpanel_token')

        # Internal analytics
        self.internal_enabled = self.config.get('internal_enabled', True)
        self.internal_storage = self.config.get('internal_storage', 'memory')

        # Privacy settings
        self.anonymize_ip = self.config.get('anonymize_ip', True)
        self.respect_dnt = self.config.get('respect_dnt', True)

        # Debug settings (New: For controlling tracking in debug mode)
        self.track_in_debug = self.config.get('track_in_debug', False)
        self.analytics_salt = self.config.get('analytics_salt', 'change-this-salt')


    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        config = {
            # Google Analytics
            'ga_enabled': os.environ.get('ANALYTICS_GA_ENABLED', 'false').lower() == 'true',
            'ga_measurement_id': os.environ.get('ANALYTICS_GA_MEASUREMENT_ID'),
            'ga_api_secret': os.environ.get('ANALYTICS_GA_API_SECRET'),

            # Mixpanel
            'mixpanel_enabled': os.environ.get('ANALYTICS_MIXPANEL_ENABLED', 'false').lower() == 'true',
            'mixpanel_token': os.environ.get('ANALYTICS_MIXPANEL_TOKEN'),

            # Internal analytics
            'internal_enabled': os.environ.get('ANALYTICS_INTERNAL_ENABLED', 'true').lower() == 'true',
            'internal_storage': os.environ.get('ANALYTICS_INTERNAL_STORAGE', 'memory'),

            # Privacy settings
            'anonymize_ip': os.environ.get('ANALYTICS_ANONYMIZE_IP', 'true').lower() == 'true',
            'respect_dnt': os.environ.get('ANALYTICS_RESPECT_DNT', 'true').lower() == 'true',

            # Debug settings
            'track_in_debug': os.environ.get('ANALYTICS_TRACK_IN_DEBUG', 'false').lower() == 'true',
            'analytics_salt': os.environ.get('ANALYTICS_SALT', 'change-this-salt')
        }

        return cls(config)

# ===== User Identification =====

def anonymize_ip_address(ip_address: Optional[str]) -> Optional[str]:
    """Anonymize IP address by removing last octet."""
    if not ip_address or ip_address == '127.0.0.1':
        return ip_address

    # IPv4
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"

    # IPv6 - Basic anonymization, might need refinement based on specific requirements
    if ':' in ip_address:
        # Example: Keep first segment
        return ip_address.split(':')[0] + '::'

    return ip_address

def generate_anonymous_id(ip_address: Optional[str], user_agent: Optional[str], salt: str) -> str:
    """Generate anonymous user ID from IP and user agent."""
    # Create a hash of IP and user agent
    data = f"{ip_address or ''}|{user_agent or ''}|{salt}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_user_id_info(request: Request, config: AnalyticsConfig, user: Optional[Dict] = None) -> Dict[str, Optional[str]]:
    """Get user identification information from request and optional authenticated user."""
    user_info: Dict[str, Optional[str]] = {}

    # Get authenticated user ID if available
    if user and 'user_id' in user:
        user_info['user_id'] = str(user['user_id']) # Ensure string
    else:
        user_info['user_id'] = None

    # Get IP address and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('User-Agent')

    # Generate anonymous ID
    user_info['anonymous_id'] = generate_anonymous_id(ip_address, user_agent, config.analytics_salt)

    # Add anonymized IP if needed
    if config.anonymize_ip:
        user_info['ip'] = anonymize_ip_address(ip_address)
    else:
        user_info['ip'] = ip_address

    return user_info

def should_track(request: Request, config: AnalyticsConfig) -> bool:
    """Determine if tracking should be performed based on request and config."""
    # Check Do Not Track header
    if config.respect_dnt and request.headers.get('DNT') == '1':
        return False

    # Check if in development/debug mode (if configured not to track)
    # Note: FastAPI doesn't have a direct equivalent to app.debug accessible here.
    # This check should ideally happen in middleware using app state or config.
    # We rely on the config flag `track_in_debug` for now.
    # if not config.track_in_debug and IS_DEBUG_MODE: # Replace IS_DEBUG_MODE with actual check
    #     return False

    return True

# ===== Event Tracking =====

class AnalyticsEvent:
    """Analytics event data structure."""

    def __init__(self, event_name: str, properties: Optional[Dict[str, Any]] = None,
                 user_id: Optional[str] = None, anonymous_id: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        """Initialize analytics event."""
        self.event_name = event_name
        self.properties = properties or {}
        self.user_id = user_id
        self.anonymous_id = anonymous_id
        self.timestamp = timestamp or datetime.utcnow()
        self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event': self.event_name,
            'properties': self.properties,
            'user_id': self.user_id,
            'anonymous_id': self.anonymous_id,
            'timestamp': self.timestamp.isoformat()
        }

class AnalyticsManager:
    """Analytics tracking and management."""

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        """Initialize analytics manager."""
        self.config = config or AnalyticsConfig.from_env() # Load config on init
        self.providers: List[AnalyticsProvider] = []

        # Initialize in-memory storage
        self._events: List[Dict[str, Any]] = []

        # Initialize providers based on config
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize analytics providers based on configuration."""
        self.providers = [] # Reset providers
        if self.config.ga_enabled and self.config.ga_measurement_id and self.config.ga_api_secret:
            self.providers.append(GoogleAnalyticsProvider(
                self.config.ga_measurement_id,
                self.config.ga_api_secret
            ))
            logger.info("Google Analytics provider initialized.")
        elif self.config.ga_enabled:
             logger.warning("Google Analytics enabled but Measurement ID or API Secret missing.")

        if self.config.mixpanel_enabled and self.config.mixpanel_token:
            self.providers.append(MixpanelProvider(
                self.config.mixpanel_token
            ))
            logger.info("Mixpanel provider initialized.")
        elif self.config.mixpanel_enabled:
             logger.warning("Mixpanel enabled but Token missing.")

    # Removed init_app and _setup_request_tracking (Flask-specific)
    # TODO: Implement request tracking using FastAPI middleware.
    # The middleware should capture request/response details and call analytics.track().
    # Example middleware structure:
    # class AnalyticsMiddleware(BaseHTTPMiddleware):
    #     async def dispatch(self, request: Request, call_next):
    #         start_time = time.time()
    #         # TODO: Get user info if authentication middleware runs before this
    #         user = getattr(request.state, 'user', None) # Example: if auth middleware sets request.state.user
    #
    #         response = await call_next(request)
    #
    #         duration_ms = int((time.time() - start_time) * 1000)
    #         # TODO: Get analytics manager instance (e.g., via dependency or global)
    #         # analytics_manager.track_request(request, response, user, duration_ms)
    #         return response

    def track(self, event_name: str, request: Request, # Added request
             properties: Optional[Dict[str, Any]] = None,
             user: Optional[Dict] = None) -> Optional[str]: # Added user, return Optional[str]
        """Track an analytics event."""
        # Skip if tracking should not be performed
        if not should_track(request, self.config):
            logger.debug("Tracking skipped due to config/DNT header.")
            return None # Return None if not tracked

        # Get user identification
        user_info = get_user_id_info(request, self.config, user)

        # Create event
        event = AnalyticsEvent(
            event_name=event_name,
            properties=properties,
            user_id=user_info.get('user_id'),
            anonymous_id=user_info.get('anonymous_id')
        )

        # Store event internally if enabled
        if self.config.internal_enabled:
            self._store_event(event)

        # Send to providers
        # TODO: Consider running provider calls asynchronously (e.g., using asyncio.gather)
        for provider in self.providers:
            try:
                # Assuming provider methods are now async
                # await provider.track(event)
                provider.track(event) # Keeping sync for now, needs review if providers become async
            except Exception as e:
                logger.error(f"Error tracking event with {type(provider).__name__}: {str(e)}", exc_info=True)

        return event.event_id

    def identify(self, user_id: str, request: Request, # Added request
                 traits: Optional[Dict[str, Any]] = None) -> None:
        """Identify a user with traits."""
        # Skip if tracking should not be performed
        if not should_track(request, self.config):
             logger.debug("Identify skipped due to config/DNT header.")
             return

        # Get anonymous ID
        # Pass None for user as identify is usually called with the known user_id
        user_info = get_user_id_info(request, self.config, None)
        anonymous_id = user_info.get('anonymous_id')

        # Send to providers
        # TODO: Consider running provider calls asynchronously
        for provider in self.providers:
            try:
                 # Assuming provider methods are now async
                 # await provider.identify(user_id, traits or {}, anonymous_id)
                 provider.identify(user_id, traits or {}, anonymous_id) # Keeping sync for now
            except Exception as e:
                logger.error(f"Error identifying user with {type(provider).__name__}: {str(e)}", exc_info=True)

    def _store_event(self, event: AnalyticsEvent) -> None:
        """Store event internally."""
        storage_type = self.config.internal_storage

        if storage_type == 'memory':
            # Store in memory
            self._events.append(event.to_dict())

            # Limit memory storage size
            max_events = 1000
            if len(self._events) > max_events:
                self._events = self._events[-max_events:]
        # TODO: Implement other storage types like 'file' or 'database' if needed

# ===== Analytics Providers =====

class AnalyticsProvider:
    """Base class for analytics providers."""

    async def track(self, event: AnalyticsEvent) -> None: # Made async
        """Track an event."""
        raise NotImplementedError

    async def identify(self, user_id: str, traits: Dict[str, Any], # Made async
                 anonymous_id: Optional[str] = None) -> None:
        """Identify a user."""
        raise NotImplementedError

class GoogleAnalyticsProvider(AnalyticsProvider):
    """Google Analytics 4 provider."""

    def __init__(self, measurement_id: str, api_secret: str): # Made api_secret required
        """Initialize Google Analytics provider."""
        if not measurement_id or not api_secret:
             raise ValueError("GA Measurement ID and API Secret are required.")
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.base_url = 'https://www.google-analytics.com/mp/collect'
        # Use an async client for non-blocking I/O
        self.client = httpx.AsyncClient(timeout=10.0) # Added timeout

    async def track(self, event: AnalyticsEvent) -> None: # Made async
        """Track an event with Google Analytics."""
        # Build GA4 event
        ga_event = {
            'name': event.event_name,
            'params': {}
        }

        # Add event parameters
        for key, value in event.properties.items():
            # GA4 has restrictions on parameter names and values
            if isinstance(value, (str, int, float, bool)):
                ga_event['params'][key] = value
            elif value is None:
                 continue # Skip None values
            else:
                 # Convert other types to string, log warning
                 logger.debug(f"Converting GA event param '{key}' to string: {value}")
                 ga_event['params'][key] = str(value)


        # Build request payload
        payload = {
            'client_id': event.anonymous_id or str(uuid.uuid4()), # GA requires client_id
            'events': [ga_event]
        }

        # Add user ID if available
        if event.user_id:
            payload['user_id'] = event.user_id

        # Build URL
        url = f"{self.base_url}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        # Send request asynchronously
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            logger.debug(f"GA track event '{event.event_name}' sent successfully.")
        except httpx.HTTPStatusError as e:
             logger.warning(f"Google Analytics track error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Google Analytics track request failed: {str(e)}")
        except Exception as e:
             logger.error(f"Unexpected error sending to Google Analytics track: {str(e)}", exc_info=True)

    async def identify(self, user_id: str, traits: Dict[str, Any], # Made async
                 anonymous_id: Optional[str] = None) -> None:
        """Identify a user with Google Analytics."""
        # GA4 uses user properties, set via a special event or config call.
        # Sending an event with user_properties is common.
        user_properties_payload = {}
        for key, value in traits.items():
             if isinstance(value, (str, int, float, bool)):
                 user_properties_payload[key] = {"value": value}
             elif value is None:
                 continue
             else:
                 logger.debug(f"Converting GA user property '{key}' to string: {value}")
                 user_properties_payload[key] = {"value": str(value)}

        if not user_properties_payload:
             logger.debug("No valid traits to send for GA identify.")
             return

        payload = {
            'client_id': anonymous_id or str(uuid.uuid4()), # Use anonymous_id if available
            'user_id': user_id,
            'user_properties': user_properties_payload
        }
        url = f"{self.base_url}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.debug(f"GA identify for user '{user_id}' sent successfully.")
        except httpx.HTTPStatusError as e:
            logger.warning(f"Google Analytics user properties error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Google Analytics user properties request failed: {str(e)}")
        except Exception as e:
             logger.error(f"Unexpected error sending GA user properties: {str(e)}", exc_info=True)


class MixpanelProvider(AnalyticsProvider):
    """Mixpanel analytics provider."""

    def __init__(self, token: str):
        """Initialize Mixpanel provider."""
        if not token:
             raise ValueError("Mixpanel token is required.")
        self.token = token
        self.base_url = 'https://api.mixpanel.com'
        # Use an async client
        self.client = httpx.AsyncClient(timeout=10.0)

    async def track(self, event: AnalyticsEvent) -> None: # Made async
        """Track an event with Mixpanel."""
        # Build Mixpanel event
        mp_event = {
            'event': event.event_name,
            'properties': {
                'token': self.token,
                'time': int(event.timestamp.timestamp()),
                'distinct_id': event.user_id or event.anonymous_id or str(uuid.uuid4()),
                '$insert_id': event.event_id,
                # Add anonymous ID if user ID is present for aliasing potential
                '$device_id': event.anonymous_id if event.user_id and event.anonymous_id else None,
            }
        }
        # Remove None values from properties base
        mp_event['properties'] = {k: v for k, v in mp_event['properties'].items() if v is not None}


        # Add event properties
        mp_event['properties'].update(event.properties)

        # Send request asynchronously
        try:
            response = await self.client.post(
                f"{self.base_url}/track",
                json=[mp_event] # Mixpanel track expects a list
            )
            response.raise_for_status()
            logger.debug(f"Mixpanel track event '{event.event_name}' sent successfully.")
        except httpx.HTTPStatusError as e:
            logger.warning(f"Mixpanel track error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Mixpanel track request failed: {str(e)}")
        except Exception as e:
             logger.error(f"Unexpected error sending to Mixpanel track: {str(e)}", exc_info=True)

    async def identify(self, user_id: str, traits: Dict[str, Any], # Made async
                 anonymous_id: Optional[str] = None) -> None:
        """Identify a user with Mixpanel."""
        # Build Mixpanel profile update
        profile = {
            '$token': self.token,
            '$distinct_id': user_id,
            '$set': traits
        }

        # Send request asynchronously
        try:
            response = await self.client.post(
                f"{self.base_url}/engage#profile-set", # Use correct endpoint
                json=[profile] # Engage expects a list
            )
            response.raise_for_status()
            logger.debug(f"Mixpanel identify for user '{user_id}' sent successfully.")

            # If anonymous_id is provided, create an alias
            if anonymous_id:
                 await self._create_alias(user_id, anonymous_id)

        except httpx.HTTPStatusError as e:
            logger.warning(f"Mixpanel engage error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Mixpanel engage request failed: {str(e)}")
        except Exception as e:
             logger.error(f"Unexpected error sending to Mixpanel engage: {str(e)}", exc_info=True)

    async def _create_alias(self, user_id: str, anonymous_id: str):
         """Create an alias in Mixpanel."""
         alias_event = {
             "event": "$create_alias",
             "properties": {
                 "distinct_id": anonymous_id,
                 "alias": user_id,
                 "token": self.token
             }
         }
         try:
            response = await self.client.post(
                f"{self.base_url}/track", # Alias uses track endpoint
                json=[alias_event]
            )
            response.raise_for_status()
            logger.debug(f"Mixpanel alias created: {anonymous_id} -> {user_id}")
         except httpx.HTTPStatusError as e:
            logger.warning(f"Mixpanel alias error: {e.response.status_code} - {e.response.text}")
         except httpx.RequestError as e:
            logger.error(f"Mixpanel alias request failed: {str(e)}")
         except Exception as e:
             logger.error(f"Unexpected error sending Mixpanel alias: {str(e)}", exc_info=True)


# Initialize analytics manager instance
# Configuration will be loaded from environment variables by default
# This instance can be imported and used in FastAPI dependencies or middleware
analytics = AnalyticsManager()

# Removed init_analytics (Flask-specific)
# TODO: Ensure AnalyticsManager is configured correctly during FastAPI app startup.
# This might involve explicitly passing a config object or ensuring env vars are set.
# TODO: Implement FastAPI middleware for automatic request tracking using the 'analytics' instance.
