import pytest
import os
from unittest.mock import patch, AsyncMock

from modules.guide_agent import GuideAgentManager

# Sample test data
SAMPLE_MARKET_DATA = {
    "top_performing_models": [
        {
            "name": "Test Model",
            "type": "test_type",
            "potential_revenue": 1000.0,
            "implementation_difficulty": 5,
            "market_saturation": 5,
            "required_apis": ["Test API"]
        }
    ],
    "trending_keywords": ["test"],
    "target_demographics": ["testers"],
    "revenue_generating_features": ["test feature"]
}

@pytest.fixture
def guide_agent():
    """Create a GuideAgentManager instance for testing."""
    # Use a mock API key for tests
    return GuideAgentManager(api_key="test_api_key")

@pytest.mark.asyncio
async def test_analyze_market(guide_agent):
    """Test the analyze_market method."""
    # Mock the agent run method
    with patch.object(guide_agent.guide_agent, 'run', new_callable=AsyncMock) as mock_run:
        # Configure the mock to return a valid result
        mock_run.return_value.data = "Market analysis result"

        # Call the method
        result = await guide_agent.analyze_market("digital-products", "test_user")

        # Check that the agent was called correctly
        assert mock_run.call_count == 2

        # Check the result
        assert "analysis" in result
        assert result["analysis"] == "Market analysis result"
        assert "segment" in result
        assert result["segment"] == "digital-products"

@pytest.mark.asyncio
async def test_identify_features(guide_agent):
    """Test the identify_features method."""
    # Mock the agent run method
    with patch.object(guide_agent.guide_agent, 'run', new_callable=AsyncMock) as mock_run:
        # Configure the mock to return a valid result
        mock_run.return_value.data = "Feature identification result"

        # Call the method
        result = await guide_agent.identify_features("Test Model", SAMPLE_MARKET_DATA, "test_user")

        # Check that the agent was called correctly
        assert mock_run.call_count == 1

        # Check the result format
        assert isinstance(result, list)
        assert len(result) > 0
        assert "feature_name" in result[0]
        assert "description" in result[0]
        assert "revenue_impact" in result[0]

@pytest.mark.asyncio
async def test_create_instructions(guide_agent):
    """Test the create_instructions method."""
    # Sample data for testing
    business_model = {
        "name": "Test Model",
        "type": "test_type",
        "potential_revenue": 1000.0,
        "implementation_difficulty": 5,
        "market_saturation": 5,
        "required_apis": ["Test API"]
    }

    features = [
        {"feature_name": "Test Feature", "description": "Test description"}
    ]

    # Mock the agent run method
    with patch.object(guide_agent.guide_agent, 'run', new_callable=AsyncMock) as mock_run:
        # Configure the mock to return a valid result
        mock_run.return_value.data = "Instruction result"

        # Call the method
        result = await guide_agent.create_instructions(business_model, features, "test_user")

        # Check that the agent was called correctly
        assert mock_run.call_count == 1

        # Check the result
        assert "instructions" in result
        assert result["instructions"] == "Instruction result"
        assert "business_model" in result
        assert "features" in result

@pytest.mark.asyncio
async def test_identify_human_tasks(guide_agent):
    """Test the identify_human_tasks method."""
    # Sample data for testing
    business_model = {
        "name": "Test Model",
        "type": "test_type",
        "required_apis": ["Test API"]
    }

    features = [
        {"feature_name": "Test Feature", "description": "Test description"}
    ]

    # Mock the agent run method
    with patch.object(guide_agent.guide_agent, 'run', new_callable=AsyncMock) as mock_run:
        # Configure the mock to return a valid result
        mock_run.return_value.data = "Human tasks result"

        # Call the method
        result = await guide_agent.identify_human_tasks(business_model, features, "test_user")

        # Check that the agent was called correctly
        assert mock_run.call_count == 1

        # Check the result
        assert isinstance(result, list)