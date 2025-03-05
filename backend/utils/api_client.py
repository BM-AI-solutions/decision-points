import os
import json
from typing import Dict, Any, Optional, List, Union, Tuple
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import setup_logger

logger = setup_logger('utils.api_client')

class APIClient:
    """Client for making API requests to external services."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize the API client.

        Args:
            base_url: Base URL for API requests
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL (will be joined with base_url if relative)
            params: Query parameters
            data: Request body data
            headers: Request headers
            auth: Authentication tuple (username, password)

        Returns:
            Response data as dictionary
        """
        # Prepare URL
        if not url.startswith(('http://', 'https://')) and self.base_url:
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

        # Prepare headers
        request_headers = {'Content-Type': 'application/json'}
        if self.api_key:
            request_headers['Authorization'] = f'Bearer {self.api_key}'
        if headers:
            request_headers.update(headers)

        try:
            # Make request
            logger.debug(f"Making {method} request to {url}")
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                auth=auth
            )

            # Check for successful response
            response.raise_for_status()

            # Parse response
            if response.headers.get('Content-Type', '').startswith('application/json'):
                return response.json()
            else:
                return {'text': response.text}

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")

            # Try to parse error response
            error_data = {'status_code': e.response.status_code}
            try:
                error_json = e.response.json()
                error_data.update(error_json)
            except ValueError:
                error_data['text'] = e.response.text

            raise APIError(f"HTTP error: {e.response.status_code}", error_data)

        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIError(f"Request error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request('POST', url, **kwargs)

    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request('PUT', url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request('DELETE', url, **kwargs)

class APIError(Exception):
    """Error raised when an API request fails."""

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.data = data or {}