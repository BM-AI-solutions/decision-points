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
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps

from flask import request, g, current_app, Response, jsonify

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
        }
        
        return cls(config)

# ===== User Identification =====

def anonymize_ip_address(ip_address: str) -> str:
    """Anonymize IP address by removing last octet."""
    if not ip_address or ip_address == '127.0.0.1':
        return ip_address
    
    # IPv4
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    
    # IPv6
    if ':' in ip_address:
        return ip_address.split(':')[0] + ':0:0:0:0:0:0:0'
    
    return ip_address

def generate_anonymous_id(ip_address: str, user_agent: str) -> str:
    """Generate anonymous user ID from IP and user agent."""
    # Create a hash of IP and user agent
    data = f"{ip_address}|{user_agent}|{os.environ.get('ANALYTICS_SALT', 'change-this-salt')}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_user_id() -> Dict[str, str]:
    """Get user identification information."""
    user_info = {}
    
    # Try to get authenticated user ID
    if hasattr(g, 'user_id'):
        user_info['user_id'] = g.user_id
    
    # Get IP address and user agent
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    # Generate anonymous ID
    user_info['anonymous_id'] = generate_anonymous_id(ip_address, user_agent)
    
    # Add anonymized IP if needed
    config = getattr(current_app, 'analytics_config', AnalyticsConfig())
    if config.anonymize_ip:
        user_info['ip'] = anonymize_ip_address(ip_address)
    else:
        user_info['ip'] = ip_address
    
    return user_info

def should_track() -> bool:
    """Determine if tracking should be performed."""
    config = getattr(current_app, 'analytics_config', AnalyticsConfig())
    
    # Check Do Not Track header
    if config.respect_dnt and request.headers.get('DNT') == '1':
        return False
    
    # Check if in development mode
    if current_app.debug and not os.environ.get('ANALYTICS_TRACK_IN_DEBUG', 'false').lower() == 'true':
        return False
    
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
    
    def __init__(self, app=None, config: Optional[AnalyticsConfig] = None):
        """Initialize analytics manager."""
        self.config = config or AnalyticsConfig()
        self.providers = []
        
        # Initialize in-memory storage
        self._events = []
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        # Store config on app
        app.analytics_config = self.config
        
        # Initialize providers
        if self.config.ga_enabled and self.config.ga_measurement_id:
            self.providers.append(GoogleAnalyticsProvider(
                self.config.ga_measurement_id,
                self.config.ga_api_secret
            ))
        
        if self.config.mixpanel_enabled and self.config.mixpanel_token:
            self.providers.append(MixpanelProvider(
                self.config.mixpanel_token
            ))
        
        # Register extension with app
        app.extensions['analytics'] = self
        
        # Set up request tracking
        self._setup_request_tracking(app)
    
    def _setup_request_tracking(self, app):
        """Set up automatic request tracking."""
        @app.before_request
        def track_request_start():
            g.request_start_time = time.time()
        
        @app.after_request
        def track_request(response):
            # Skip if tracking should not be performed
            if not should_track():
                return response
            
            # Skip for certain paths
            skip_paths = ['/static/', '/health', '/favicon.ico']
            if any(request.path.startswith(path) for path in skip_paths):
                return response
            
            # Calculate request duration
            duration_ms = 0
            if hasattr(g, 'request_start_time'):
                duration_ms = int((time.time() - g.request_start_time) * 1000)
            
            # Track page view or API request
            if request.path.startswith('/api/'):
                # API request
                self.track(
                    'api_request',
                    {
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                        'duration_ms': duration_ms
                    }
                )
            else:
                # Page view
                self.track(
                    'page_view',
                    {
                        'page_path': request.path,
                        'referrer': request.referrer,
                        'duration_ms': duration_ms
                    }
                )
            
            return response
    
    def track(self, event_name: str, properties: Optional[Dict[str, Any]] = None,
             user_id: Optional[str] = None, anonymous_id: Optional[str] = None) -> str:
        """Track an analytics event."""
        # Skip if tracking should not be performed
        if not should_track():
            return str(uuid.uuid4())  # Return dummy event ID
        
        # Get user identification
        user_info = get_user_id()
        
        if not user_id and 'user_id' in user_info:
            user_id = user_info['user_id']
        
        if not anonymous_id and 'anonymous_id' in user_info:
            anonymous_id = user_info['anonymous_id']
        
        # Create event
        event = AnalyticsEvent(
            event_name=event_name,
            properties=properties,
            user_id=user_id,
            anonymous_id=anonymous_id
        )
        
        # Store event internally if enabled
        if self.config.internal_enabled:
            self._store_event(event)
        
        # Send to providers
        for provider in self.providers:
            try:
                provider.track(event)
            except Exception as e:
                logger.error(f"Error tracking event: {str(e)}")
        
        return event.event_id
    
    def identify(self, user_id: str, traits: Optional[Dict[str, Any]] = None,
                anonymous_id: Optional[str] = None) -> None:
        """Identify a user with traits."""
        # Skip if tracking should not be performed
        if not should_track():
            return
        
        # Get anonymous ID if not provided
        if not anonymous_id:
            user_info = get_user_id()
            anonymous_id = user_info.get('anonymous_id')
        
        # Send to providers
        for provider in self.providers:
            try:
                provider.identify(user_id, traits or {}, anonymous_id)
            except Exception as e:
                logger.error(f"Error identifying user: {str(e)}")
    
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

# ===== Analytics Providers =====

class AnalyticsProvider:
    """Base class for analytics providers."""
    
    def track(self, event: AnalyticsEvent) -> None:
        """Track an event."""
        raise NotImplementedError
    
    def identify(self, user_id: str, traits: Dict[str, Any],
                anonymous_id: Optional[str] = None) -> None:
        """Identify a user."""
        raise NotImplementedError

class GoogleAnalyticsProvider(AnalyticsProvider):
    """Google Analytics 4 provider."""
    
    def __init__(self, measurement_id: str, api_secret: Optional[str] = None):
        """Initialize Google Analytics provider."""
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.base_url = 'https://www.google-analytics.com/mp/collect'
    
    def track(self, event: AnalyticsEvent) -> None:
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
        
        # Build request payload
        payload = {
            'client_id': event.anonymous_id or str(uuid.uuid4()),
            'events': [ga_event]
        }
        
        # Add user ID if available
        if event.user_id:
            payload['user_id'] = event.user_id
        
        # Build URL with API secret if available
        url = f"{self.base_url}?measurement_id={self.measurement_id}"
        if self.api_secret:
            url += f"&api_secret={self.api_secret}"
        
        # Send request
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 204 and response.status_code != 200:
                logger.warning(f"Google Analytics error: {response.status_code}")
        except Exception as e:
            logger.error(f"Google Analytics request failed: {str(e)}")
    
    def identify(self, user_id: str, traits: Dict[str, Any],
                anonymous_id: Optional[str] = None) -> None:
        """Identify a user with Google Analytics."""
        # GA4 doesn't have a specific identify method
        # We'll send a user_data event instead
        self.track(AnalyticsEvent(
            event_name='user_data',
            properties=traits,
            user_id=user_id,
            anonymous_id=anonymous_id
        ))

class MixpanelProvider(AnalyticsProvider):
    """Mixpanel analytics provider."""
    
    def __init__(self, token: str):
        """Initialize Mixpanel provider."""
        self.token = token
        self.base_url = 'https://api.mixpanel.com'
    
    def track(self, event: AnalyticsEvent) -> None:
        """Track an event with Mixpanel."""
        # Build Mixpanel event
        mp_event = {
            'event': event.event_name,
            'properties': {
                'token': self.token,
                'time': int(event.timestamp.timestamp()),
                'distinct_id': event.user_id or event.anonymous_id or str(uuid.uuid4()),
                '$insert_id': event.event_id
            }
        }
        
        # Add event properties
        for key, value in event.properties.items():
            mp_event['properties'][key] = value
        
        # Send request
        try:
            response = requests.post(
                f"{self.base_url}/track",
                data=json.dumps([mp_event]),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                logger.warning(f"Mixpanel error: {response.status_code}")
        except Exception as e:
            logger.error(f"Mixpanel request failed: {str(e)}")
    
    def identify(self, user_id: str, traits: Dict[str, Any],
                anonymous_id: Optional[str] = None) -> None:
        """Identify a user with Mixpanel."""
        # Build Mixpanel profile update
        profile = {
            '$token': self.token,
            '$distinct_id': user_id,
            '$set': traits
        }
        
        # Send request
        try:
            response = requests.post(
                f"{self.base_url}/engage",
                data=json.dumps([profile]),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                logger.warning(f"Mixpanel error: {response.status_code}")
        except Exception as e:
            logger.error(f"Mixpanel request failed: {str(e)}")

# Initialize analytics manager
analytics = AnalyticsManager()

def init_analytics(app):
    """Initialize analytics with Flask application."""
    config = AnalyticsConfig.from_env()
    analytics.init_app(app)
    return analytics
