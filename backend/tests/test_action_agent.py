import pytest
import os
from unittest.mock import patch, AsyncMock

from modules.action_agent import ActionAgentManager

@pytest.fixture
def action_agent():
    """Create an ActionAgentManager instance for testing."""
    # Use a mock API key for tests
    return ActionAgentManager(api_key="test_api_key")

@pytest.mark.asyncio
async def test_implement_business_model(action_agent):
    """Test the implement_business_model method."""
    # Sample data for testing
    instructions = {"instructions": "Test instructions"}
    business_model = {"name": "Test Model", "type": "test_type"}
    features = [{"feature_name": "Test Feature", "description": "Test description"}]

    # Mock the agent run method
    with patch.object(action_agent.action_agent, 'run', new_callable=AsyncMock) as mock_run:
        # Configure the mock to return a valid result
        mock_run.return_value.data = "Implementation result"

        # Call the method
        result = await action_agent.implement_business_model(
            instructions, 
            business_model, 
            features, 
            "test_user"
        )

        # Check that the agent was called correctly
        assert mock_run.call_count == 1

        # Check the result
        assert "implementation_result" in result
        assert result["implementation_result"] == "Implementation result"
        assert "business_model" in result
        assert "features_implemented" in result

@pytest.mark.asyncio
async def test_implement_feature(action_agent):
    """Test the implement_feature method."""
    # Sample data for testing
    feature = {
        "feature_name": "Test Feature",
        "description": "Test description",
        "implementation_steps": ["Step 1", "Step 2"],
        "required_apis": ["Test API"],
        "estimated_implementation_time": "1 hour"
    }

    service_name = "Test Service"

    # Mock the implement_feature method
    with patch('modules.action_agent.implement_feature', new_callable=AsyncMock) as mock_implement:
        # Configure the mock to return a valid result
        mock_implement.return_value = {
            "success": True,
            "action_type": "FEATURE_IMPLEMENTATION",
            "details": {"feature_name": "Test Feature"},
            "next_steps": ["Step 1"],
            "revenue_impact": 10.0
        }

        # Mock the agent run method as fallback
        with patch.object(action_agent.action_agent, 'run', new_callable=AsyncMock) as mock_run:
            # Configure the mock to return a valid result
            mock_run.return_value.data = "Feature result"

            # Call the method
            result = await action_agent.implement_feature(feature, service_name, "test_user")

            # Check the result
            assert "success" in result
            assert result["success"] is True
            assert "action_type" in result
            assert "details" in result
            assert "next_steps" in result
            assert "revenue_impact" in result

@pytest.mark.asyncio
async def test_create_branding(action_agent):
    """Test the create_branding method."""
    # Sample data for testing
    business_model_name = "Test Business Model"
    target_demographics = ["Test Demographic"]

    # Mock the create_branding method
    with patch('modules.action_agent.create_branding', new_callable=AsyncMock) as mock_branding:
        # Configure the mock to return a valid result
        mock_branding.return_value = {
            "brand_name": "TestBrand",
            "logo_url": None,
            "color_scheme": ["#FFFFFF"],
            "positioning_statement": "Test statement"
        }

        # Mock the agent run method as fallback
        with patch.object(action_agent.action_agent, 'run', new_callable=AsyncMock) as mock_run:
            # Configure the mock to return a valid result
            mock_run.return_value.data = "Branding result"

            # Call the method
            result = await action_agent.create_branding(
                business_model_name,
                target_demographics,
                "test_user"
            )

            # Check the result
            assert "brand_name" in result
            assert "color_scheme" in result
            assert "positioning_statement" in result

@pytest.mark.asyncio
async def test_deploy_system(action_agent):
    """Test the deploy_system method."""
    # Sample data for testing
    business_model_name = "Test Business Model"
    implemented_features = ["Feature 1", "Feature 2"]

    # Mock the deploy_system method
    with patch('modules.action_agent.deploy_system', new_callable=AsyncMock) as mock_deploy:
        # Configure the mock to return a valid result
        mock_deploy.return_value = {
            "deployment_url": "https://test.com",
            "status": "ACTIVE",
            "features_deployed": implemented_features,
            "monitoring_url": "https://test.com/dashboard"
        }

        # Mock the agent run method as fallback
        with patch.object(action_agent.action_agent, 'run', new_callable=AsyncMock) as mock_run:
            # Configure the mock to return a valid result
            mock_run.return_value.data = "Deployment result"

            # Call the method
            result = await action_agent.deploy_system(
                business_model_name,
                implemented_features,
                "test_user"
            )

            # Check the result
            assert "deployment_url" in result
            assert "status" in result
            assert "features_deployed" in result
            assert result["features_deployed"] == implemented_features

@pytest.mark.asyncio
async def test_calculate_cash_flow(action_agent):
    """Test the calculate_cash_flow method."""
    # Sample data for testing
    business_model_name = "Test Business Model"
    implemented_features = ["Feature 1", "Feature 2"]

    # Mock the update_cash_flow_status method
    with patch('modules.action_agent.update_cash_flow_status', new_callable=AsyncMock) as mock_cash_flow:
        # Configure the mock to return a valid result
        mock_cash_flow.return_value = {
            "revenue_streams": ["Base Sales"],
            "estimated_monthly_revenue": 1500.0,
            "payment_methods": ["Credit Card"],
            "payout_schedule": "Bi-weekly",
            "automated_percentage": 90
        }

        # Mock the agent run method as fallback
        with patch.object(action_agent.action_agent, 'run', new_callable=AsyncMock) as mock_run:
            # Configure the mock to return a valid result
            mock_run.return_value.data = "Cash flow result"

            # Call the method
            result = await action_agent.calculate_cash_flow(
                business_model_name,
                implemented_features,
                "test_user"
            )

            # Check the result
            assert "revenue_streams" in result
            assert "estimated_monthly_revenue" in result
            assert "payment_methods" in result
            assert "automated_percentage" in result