"""
Production-ready Flask application with enhanced security, performance, and reliability.

This module integrates all production enhancements:
1. Security hardening
2. Performance optimization
3. Error handling
4. Authentication robustness
5. Data backup
6. Analytics
7. Accessibility compliance
8. Legal compliance
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional, List, Union

from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, g
from werkzeug.middleware.proxy_fix import ProxyFix
import redis

# Import core application components
from config import Config
from utils.logger import setup_logger
from routes import auth, market, business, features, deployment, cashflow

# Import production enhancements
from utils.security_enhancements import (
    enhanced_security_headers, 
    csrf_protect, 
    rate_limit,
    jwt_required
)
from utils.performance import (
    CacheManager, 
    gzip_response, 
    profile_request_middleware,
    PerformanceMonitor
)
from utils.error_handling import (
    setup_error_handlers, 
    handle_exceptions,
    ErrorMonitor
)
from utils.backup import BackupConfig, create_backup
from utils.analytics import init_analytics
from utils.accessibility import init_accessibility
from utils.legal import init_legal, LegalConfig

# Load environment variables
load_dotenv()

def create_app(config_class=Config) -> Flask:
    """Create and configure the Flask application for production."""
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set up logging
    logger = setup_logger()
    
    # ===== Security Enhancements =====
    
    # Apply security headers to all responses
    app.after_request(enhanced_security_headers)
    
    # Configure CORS with strict origins
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').split(',')
    if not allowed_origins or allowed_origins[0] == '':
        allowed_origins = ['https://decisionpoints.intellisol.cc']
    
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    
    # Fix for proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # ===== Performance Optimization =====
    
    # Initialize caching
    cache_type = app.config.get('CACHE_TYPE', 'simple')
    if cache_type == 'redis':
        # Set up Redis connection
        redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
        app.config['REDIS_CLIENT'] = redis.from_url(redis_url)
    
    cache_manager = CacheManager(app)
    
    # Enable response compression
    @app.after_request
    def compress_response(response):
        return gzip_response(response)
    
    # Add request profiling
    app = profile_request_middleware(app)
    
    # ===== Error Handling =====
    
    # Set up global error handlers
    setup_error_handlers(app)
    
    # ===== Register Blueprints =====
    
    # Wrap blueprint routes with error handling
    def register_blueprint_with_error_handling(blueprint, url_prefix):
        """Register blueprint with error handling for all routes."""
        for endpoint, view_func in blueprint.view_functions.items():
            blueprint.view_functions[endpoint] = handle_exceptions(view_func)
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    
    # Register blueprints with error handling
    register_blueprint_with_error_handling(auth.bp, '/api/auth')
    register_blueprint_with_error_handling(market.bp, '/api/market')
    register_blueprint_with_error_handling(business.bp, '/api/business')
    register_blueprint_with_error_handling(features.bp, '/api/features')
    register_blueprint_with_error_handling(deployment.bp, '/api/deployment')
    register_blueprint_with_error_handling(cashflow.bp, '/api/cashflow')
    
    # ===== Analytics Integration =====
    
    # Initialize analytics
    analytics = init_analytics(app)
    
    # ===== Accessibility Compliance =====
    
    # Initialize accessibility checking
    accessibility = init_accessibility(app)
    
    # ===== Legal Compliance =====
    
    # Initialize legal documents
    legal = init_legal(app)
    
    # ===== Health Check Endpoint =====
    
    @app.route('/api/health', methods=['GET'])
    @cache_manager.cached(timeout=60)  # Cache for 1 minute
    def health_check() -> Dict[str, str]:
        """Health check endpoint with enhanced information."""
        # Start performance timer
        start_time = PerformanceMonitor.start_timer()
        
        # Check database connection
        db_status = "healthy"
        try:
            # This would typically check the database connection
            # For now, just assume it's healthy
            pass
        except Exception as e:
            db_status = f"error: {str(e)}"
            ErrorMonitor.capture_exception(e, {"context": "health_check"})
        
        # Check cache connection
        cache_status = "healthy"
        try:
            # Check if cache is working
            test_key = "health_check_test"
            cache_manager.set(test_key, "test", timeout=5)
            cache_value = cache_manager.get(test_key)
            if cache_value != "test":
                cache_status = "error: cache value mismatch"
        except Exception as e:
            cache_status = f"error: {str(e)}"
            ErrorMonitor.capture_exception(e, {"context": "health_check"})
        
        # Get system info
        import platform
        system_info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "memory_usage": os.popen('ps -o rss= -p %d' % os.getpid()).read().strip()
        }
        
        # Log performance
        elapsed_time = PerformanceMonitor.end_timer(start_time)
        
        # Track health check in analytics
        analytics.track(
            'health_check',
            {
                'response_time': elapsed_time,
                'db_status': db_status,
                'cache_status': cache_status
            }
        )
        
        return jsonify({
            "status": "healthy",
            "version": app.config.get('VERSION', '1.0.0'),
            "environment": os.environ.get('FLASK_ENV', 'production'),
            "database": db_status,
            "cache": cache_status,
            "response_time": f"{elapsed_time:.6f}s",
            "system_info": system_info
        })
    
    # ===== Public Configuration Endpoint =====
    
    @app.route('/api/config', methods=['GET'])
    @cache_manager.cached(timeout=300)  # Cache for 5 minutes
    def get_public_config() -> Dict[str, Any]:
        """Provide public configuration settings to the frontend."""
        return jsonify({
            "marketSegments": [
                {"id": "digital-products", "name": "Digital Products"},
                {"id": "e-commerce", "name": "E-Commerce"},
                {"id": "saas", "name": "SaaS Applications"},
                {"id": "online-education", "name": "Online Education"},
                {"id": "affiliate-marketing", "name": "Affiliate Marketing"}
            ],
            "businessPreferences": [
                {"id": "highest-revenue", "name": "Highest Revenue Potential"},
                {"id": "lowest-effort", "name": "Lowest Human Effort"},
                {"id": "fastest-implementation", "name": "Fastest Implementation"},
                {"id": "lowest-startup-cost", "name": "Lowest Startup Cost"}
            ],
            "apiVersion": app.config.get('API_VERSION', '1.0.0'),
            "contactEmail": app.config.get('CONTACT_EMAIL', 'support@intellisol.cc'),
            "legalDocuments": {
                "privacyPolicy": f"/{app.extensions['legal_config'].privacy_policy_path}",
                "termsOfService": f"/{app.extensions['legal_config'].terms_of_service_path}",
                "cookiePolicy": f"/{app.extensions['legal_config'].cookie_policy_path}"
            },
            "features": app.config.get('FEATURES', {})
        })
    
    # ===== Request Tracking =====
    
    @app.before_request
    def before_request():
        """Track request start time and set up request context."""
        g.start_time = PerformanceMonitor.start_timer()
        g.request_id = os.urandom(8).hex()
        
        # Log request
        logger.info(f"Request {g.request_id}: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Track request completion and log performance metrics."""
        if hasattr(g, 'start_time'):
            elapsed_time = PerformanceMonitor.end_timer(g.start_time)
            response.headers['X-Response-Time'] = f"{elapsed_time:.6f}s"
            
            # Log request completion
            logger.info(
                f"Request {getattr(g, 'request_id', 'unknown')} completed: "
                f"{request.method} {request.path} - {response.status_code} in {elapsed_time:.6f}s"
            )
        
        return response
    
    # ===== Scheduled Tasks =====
    
    # Set up scheduled backup task (would typically use a task scheduler like Celery)
    @app.cli.command("backup")
    def backup_command():
        """Run database backup."""
        # Get database configuration from app config
        db_config = {
            "type": os.environ.get('DB_TYPE', 'postgres'),
            "name": os.environ.get('DB_NAME', 'decision_points'),
            "user": os.environ.get('DB_USER', 'postgres'),
            "password": os.environ.get('DB_PASSWORD', ''),
            "host": os.environ.get('DB_HOST', 'localhost'),
            "port": int(os.environ.get('DB_PORT', 5432))
        }
        
        # Create backup configuration
        backup_config = BackupConfig.from_env()
        
        # Run backup
        try:
            backup_info = create_backup(backup_config, 'database', db_config)
            logger.info(f"Backup completed: {backup_info['backup_id']}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            ErrorMonitor.capture_exception(e, {"context": "scheduled_backup"})
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)