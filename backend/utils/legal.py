"""
Legal document utilities for production deployment.

This module provides:
1. Privacy policy generation and management
2. Terms of service generation and management
3. Cookie policy implementation
4. User consent management
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from functools import wraps

from flask import request, Response, g, current_app, render_template_string, jsonify

from utils.logger import setup_logger

# Set up module logger
logger = setup_logger('utils.legal')

# ===== Legal Document Configuration =====

class LegalConfig:
    """Legal document configuration settings."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize legal configuration."""
        self.config = config or {}
        
        # Company information
        self.company_name = self.config.get('company_name', 'Your Company Name')
        self.company_address = self.config.get('company_address', 'Your Company Address')
        self.company_email = self.config.get('company_email', 'privacy@example.com')
        self.company_website = self.config.get('company_website', 'https://example.com')
        
        # Document paths
        self.privacy_policy_path = self.config.get('privacy_policy_path', 'privacy-policy')
        self.terms_of_service_path = self.config.get('terms_of_service_path', 'terms-of-service')
        self.cookie_policy_path = self.config.get('cookie_policy_path', 'cookie-policy')
        
        # Document versions
        self.privacy_policy_version = self.config.get('privacy_policy_version', '1.0')
        self.terms_of_service_version = self.config.get('terms_of_service_version', '1.0')
        self.cookie_policy_version = self.config.get('cookie_policy_version', '1.0')
        
        # Last updated dates
        self.privacy_policy_updated = self.config.get('privacy_policy_updated', datetime.utcnow().strftime('%Y-%m-%d'))
        self.terms_of_service_updated = self.config.get('terms_of_service_updated', datetime.utcnow().strftime('%Y-%m-%d'))
        self.cookie_policy_updated = self.config.get('cookie_policy_updated', datetime.utcnow().strftime('%Y-%m-%d'))
        
        # Compliance settings
        self.gdpr_enabled = self.config.get('gdpr_enabled', True)
        self.ccpa_enabled = self.config.get('ccpa_enabled', True)
        self.require_cookie_consent = self.config.get('require_cookie_consent', True)
        
        # Data collection settings
        self.collect_analytics = self.config.get('collect_analytics', True)
        self.collect_personal_data = self.config.get('collect_personal_data', True)
        self.third_party_services = self.config.get('third_party_services', [])
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        config = {
            # Company information
            'company_name': os.environ.get('LEGAL_COMPANY_NAME', 'Your Company Name'),
            'company_address': os.environ.get('LEGAL_COMPANY_ADDRESS', 'Your Company Address'),
            'company_email': os.environ.get('LEGAL_COMPANY_EMAIL', 'privacy@example.com'),
            'company_website': os.environ.get('LEGAL_COMPANY_WEBSITE', 'https://example.com'),
            
            # Document versions
            'privacy_policy_version': os.environ.get('LEGAL_PRIVACY_POLICY_VERSION', '1.0'),
            'terms_of_service_version': os.environ.get('LEGAL_TERMS_OF_SERVICE_VERSION', '1.0'),
            'cookie_policy_version': os.environ.get('LEGAL_COOKIE_POLICY_VERSION', '1.0'),
            
            # Compliance settings
            'gdpr_enabled': os.environ.get('LEGAL_GDPR_ENABLED', 'true').lower() == 'true',
            'ccpa_enabled': os.environ.get('LEGAL_CCPA_ENABLED', 'true').lower() == 'true',
            'require_cookie_consent': os.environ.get('LEGAL_REQUIRE_COOKIE_CONSENT', 'true').lower() == 'true',
        }
        
        # Parse third-party services
        third_party_services_str = os.environ.get('LEGAL_THIRD_PARTY_SERVICES', '')
        if third_party_services_str:
            config['third_party_services'] = [s.strip() for s in third_party_services_str.split(',')]
        
        return cls(config)

# ===== Privacy Policy =====

def generate_privacy_policy(config: LegalConfig) -> str:
    """Generate privacy policy HTML."""
    return f"""
    <div class="privacy-policy">
        <h1>Privacy Policy</h1>
        <p>Last Updated: {config.privacy_policy_updated}</p>
        <p>Version: {config.privacy_policy_version}</p>
        
        <h2>1. Introduction</h2>
        <p>Welcome to {config.company_name}'s Privacy Policy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services.</p>
        
        <h2>2. Information We Collect</h2>
        <h3>2.1 Personal Information</h3>
        <p>We may collect personal information that you voluntarily provide to us when you register for an account, sign up for our newsletter, contact our customer support, participate in surveys or promotions, or make purchases through our platform.</p>
        
        <h3>2.2 Automatically Collected Information</h3>
        <p>When you access our website, we may automatically collect certain information about your device and usage, including IP address, browser type, operating system, device information, usage patterns, and referring URLs.</p>
        
        <h2>3. How We Use Your Information</h2>
        <p>We may use the information we collect for various purposes, including providing and maintaining our services, processing transactions, sending administrative information, sending marketing communications, responding to inquiries, improving our website, and protecting our rights.</p>
        
        <h2>4. How We Share Your Information</h2>
        <p>We may share your information with service providers, business partners, affiliated companies, third parties in connection with business transactions, and law enforcement when required by law.</p>
        
        <h2>5. Your Rights</h2>
        {
            """
            <h3>5.1 GDPR Rights (European Users)</h3>
            <p>If you are located in the European Economic Area (EEA), you have certain rights under the General Data Protection Regulation (GDPR), including the right to access, rectify, erase, restrict processing, data portability, and object to processing.</p>
            """ if config.gdpr_enabled else ""
        }
        
        {
            """
            <h3>5.2 CCPA Rights (California Residents)</h3>
            <p>If you are a California resident, you have certain rights under the California Consumer Privacy Act (CCPA), including the right to know what personal information we collect, request deletion, opt-out of sale, and non-discrimination.</p>
            """ if config.ccpa_enabled else ""
        }
        
        <h2>6. Contact Us</h2>
        <p>If you have any questions or concerns about this Privacy Policy, please contact us at:</p>
        <p>{config.company_name}<br>
        {config.company_address}<br>
        Email: {config.company_email}</p>
    </div>
    """

# ===== Terms of Service =====

def generate_terms_of_service(config: LegalConfig) -> str:
    """Generate terms of service HTML."""
    return f"""
    <div class="terms-of-service">
        <h1>Terms of Service</h1>
        <p>Last Updated: {config.terms_of_service_updated}</p>
        <p>Version: {config.terms_of_service_version}</p>
        
        <h2>1. Agreement to Terms</h2>
        <p>By accessing or using our website and services, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>
        
        <h2>2. Use License</h2>
        <p>Permission is granted to temporarily access the materials on {config.company_name}'s website for personal, non-commercial use.</p>
        
        <h2>3. User Accounts</h2>
        <p>When you create an account with us, you must provide accurate information. You are responsible for safeguarding your password and for all activities that occur under your account.</p>
        
        <h2>4. Prohibited Uses</h2>
        <p>You may use our services only for lawful purposes and in accordance with these Terms.</p>
        
        <h2>5. Intellectual Property</h2>
        <p>The content, features, and functionality of our services are owned by {config.company_name} and are protected by copyright, trademark, and other intellectual property laws.</p>
        
        <h2>6. Disclaimer of Warranties</h2>
        <p>Our services are provided "as is" and "as available" without any warranties of any kind.</p>
        
        <h2>7. Limitation of Liability</h2>
        <p>In no event shall {config.company_name} be liable for any indirect, incidental, special, consequential, or punitive damages.</p>
        
        <h2>8. Contact Us</h2>
        <p>If you have any questions about these Terms, please contact us at:</p>
        <p>{config.company_name}<br>
        {config.company_address}<br>
        Email: {config.company_email}</p>
    </div>
    """

# ===== Cookie Policy =====

def generate_cookie_policy(config: LegalConfig) -> str:
    """Generate cookie policy HTML."""
    return f"""
    <div class="cookie-policy">
        <h1>Cookie Policy</h1>
        <p>Last Updated: {config.cookie_policy_updated}</p>
        <p>Version: {config.cookie_policy_version}</p>
        
        <h2>1. What Are Cookies</h2>
        <p>Cookies are small text files that are stored on your device when you visit a website.</p>
        
        <h2>2. How We Use Cookies</h2>
        <p>We use cookies for various purposes, including:</p>
        <ul>
            <li><strong>Essential Cookies:</strong> These cookies are necessary for the website to function properly.</li>
            <li><strong>Performance Cookies:</strong> These cookies allow us to count visits and traffic sources.</li>
            <li><strong>Functionality Cookies:</strong> These cookies enable enhanced functionality and personalization.</li>
            <li><strong>Targeting Cookies:</strong> These cookies may be set through our site by our advertising partners.</li>
        </ul>
        
        <h2>3. Third-Party Cookies</h2>
        <p>In addition to our own cookies, we may also use various third-party cookies.</p>
        
        <h2>4. Managing Cookies</h2>
        <p>Most web browsers allow you to control cookies through their settings preferences.</p>
        
        <h2>5. Contact Us</h2>
        <p>If you have any questions about this Cookie Policy, please contact us at:</p>
        <p>{config.company_name}<br>
        {config.company_address}<br>
        Email: {config.company_email}</p>
    </div>
    """

# ===== User Consent Management =====

class ConsentManager:
    """User consent management."""
    
    def __init__(self, config: LegalConfig):
        """Initialize consent manager."""
        self.config = config
    
    def get_consent_cookie_name(self, consent_type: str) -> str:
        """Get cookie name for consent type."""
        return f"{consent_type.lower()}_consent"
    
    def get_consent_from_cookie(self, consent_type: str) -> Optional[Dict[str, Any]]:
        """Get consent data from cookie."""
        cookie_name = self.get_consent_cookie_name(consent_type)
        consent_cookie = request.cookies.get(cookie_name)
        
        if not consent_cookie:
            return None
        
        try:
            return json.loads(consent_cookie)
        except json.JSONDecodeError:
            return None
    
    def get_user_consent(self, consent_type: str) -> Dict[str, Any]:
        """Get user consent data."""
        # Get from cookie
        consent = self.get_consent_from_cookie(consent_type)
        if consent:
            return consent
        
        # Default consent (not given)
        return {
            'given': False,
            'timestamp': None,
            'version': None,
            'preferences': {}
        }
    
    def set_consent_cookie(self, response: Response, consent_type: str, consent_data: Dict[str, Any]) -> Response:
        """Set consent cookie on response."""
        cookie_name = self.get_consent_cookie_name(consent_type)
        max_age = 365 * 24 * 60 * 60  # 1 year in seconds
        
        response.set_cookie(
            cookie_name,
            json.dumps(consent_data),
            max_age=max_age,
            httponly=True,
            secure=request.is_secure,
            samesite='Lax'
        )
        
        return response
    
    def record_consent(self, consent_type: str, preferences: Dict[str, bool],
                      response: Optional[Response] = None) -> Optional[Response]:
        """Record user consent."""
        # Create consent data
        consent_data = {
            'given': True,
            'timestamp': datetime.utcnow().isoformat(),
            'version': getattr(self.config, f"{consent_type.lower()}_policy_version", '1.0'),
            'preferences': preferences
        }
        
        # Store in cookie if response provided
        if response:
            return self.set_consent_cookie(response, consent_type, consent_data)
        
        return None
    
    def check_consent(self, consent_type: str, preference: Optional[str] = None) -> bool:
        """Check if user has given consent."""
        consent = self.get_user_consent(consent_type)
        
        # Check if consent is given
        if not consent.get('given', False):
            return False
        
        # Check specific preference if provided
        if preference:
            return consent.get('preferences', {}).get(preference, False)
        
        return True
    
    def generate_consent_banner_html(self, consent_type: str = 'cookie') -> str:
        """Generate HTML for consent banner."""
        return f"""
        <div id="{consent_type}-consent-banner" class="consent-banner">
            <div class="consent-banner-content">
                <h3>We use cookies</h3>
                <p>We use cookies and similar technologies to provide you with a better experience.</p>
                <div class="consent-actions">
                    <button id="accept-all-cookies" class="consent-button primary">Accept All</button>
                    <button id="reject-cookies" class="consent-button tertiary">Reject Non-Essential</button>
                </div>
                <p class="consent-footer">
                    For more information, please read our <a href="/{self.config.cookie_policy_path}">Cookie Policy</a>.
                </p>
            </div>
        </div>
        """

# ===== Flask Integration =====

def init_legal(app, config: Optional[LegalConfig] = None):
    """Initialize legal documents with Flask application."""
    if config is None:
        config = LegalConfig.from_env()
    
    consent_manager = ConsentManager(config)
    
    # Store in app extensions
    app.extensions['legal_config'] = config
    app.extensions['consent_manager'] = consent_manager
    
    # Register routes for legal documents
    @app.route(f"/{config.privacy_policy_path}")
    def privacy_policy():
        return render_template_string(generate_privacy_policy(config))
    
    @app.route(f"/{config.terms_of_service_path}")
    def terms_of_service():
        return render_template_string(generate_terms_of_service(config))
    
    @app.route(f"/{config.cookie_policy_path}")
    def cookie_policy():
        return render_template_string(generate_cookie_policy(config))
    
    # API endpoint for recording consent
    @app.route('/api/consent/<consent_type>', methods=['POST'])
    def record_consent(consent_type):
        data = request.json
        preferences = data.get('preferences', {})
        
        response = jsonify({'success': True})
        consent_manager.record_consent(consent_type, preferences, response)
        
        return response
    
    # Make consent manager available in templates
    @app.context_processor
    def inject_consent_manager():
        return {
            'consent_manager': consent_manager,
            'legal_config': config
        }
    
    return consent_manager

# Initialize with default configuration
legal_config = LegalConfig()
consent_manager = ConsentManager(legal_config)
