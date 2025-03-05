import pytest
import json
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data

def test_config_endpoint(client):
    """Test the configuration endpoint."""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'marketSegments' in data
    assert 'businessPreferences' in data
    assert 'apiVersion' in data

def test_market_analyze_missing_segment(client):
    """Test market analysis with missing segment."""
    response = client.post('/api/market/analyze', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Market segment is required'

@pytest.mark.asyncio
async def test_market_analyze(client):
    """Test the market analysis endpoint."""
    # Mock the GuideAgentManager.analyze_market method
    with patch('modules.guide_agent.GuideAgentManager.analyze_market', new_callable=AsyncMock) as mock_analyze:
        # Configure the mock to return a valid result
        mock_analyze.return_value = {
            "analysis": "Market analysis result",
            "market_data": "Market data",
            "segment": "digital-products"
        }

        # Make a request to the endpoint
        response = client.post('/api/market/analyze', json={"market_segment": "digital-products"})

        # Check the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'market_analysis' in data
        assert 'user_id' in data

def test_auth_register(client):
    """Test the user registration endpoint."""
    response = client.post('/api/auth/register', json={
        "email": "test@example.com",
        "password": "test123",
        "name": "Test User"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'user' in data
    assert data['user']['email'] == "test@example.com"
    assert data['user']['name'] == "Test User"
    assert 'credits' in data['user']

def test_auth_login(client):
    """Test the user login endpoint."""
    # Register a user first
    client.post('/api/auth/register', json={
        "email": "login@example.com",
        "password": "test123",
        "name": "Login User"
    })

    # Try logging in
    response = client.post('/api/auth/login', json={
        "email": "login@example.com",
        "password": "test123"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'token' in data
    assert 'user' in data
    assert data['user']['email'] == "login@example.com"

def test_auth_login_invalid(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        "email": "invalid@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_auth_profile_no_auth(client):
    """Test profile endpoint without authentication."""
    response = client.get('/api/auth/profile')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Authorization required'

def test_auth_profile(client):
    """Test the user profile endpoint with authentication."""
    # Register a user first
    register_response = client.post('/api/auth/register', json={
        "email": "profile@example.com",
        "password": "test123",
        "name": "Profile User"
    })
    register_data = json.loads(register_response.data)
    user_id = register_data['user']['id']

    # Login to get a token
    login_response = client.post('/api/auth/login', json={
        "email": "profile@example.com",
        "password": "test123"
    })
    login_data = json.loads(login_response.data)
    token = login_data['token']

    # Make an authenticated request
    response = client.get('/api/auth/profile', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'user' in data
    assert data['user']['id'] == user_id
    assert data['user']['email'] == "profile@example.com"