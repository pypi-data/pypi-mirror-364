"""
HTTP client utilities for Teams bots
"""

import httpx
from typing import Dict, Any, Optional, Union
import logging
import json
import asyncio

# Global client instances and lock
_clients = {}
_client_lock = asyncio.Lock()


async def get_pooled_client(
    base_url: str = "",
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    pool_key: str = "default",
    max_connections: int = 100,
    max_keepalive_connections: int = 20,
) -> httpx.AsyncClient:
    """
    Get or create a shared HTTP client

    Args:
        base_url: Base URL for all requests
        headers: Default headers for all requests
        timeout: Default request timeout in seconds
        pool_key: Identifier for this client pool
        max_connections: Maximum number of connections
        max_keepalive_connections: Maximum number of idle keepalive connections

    Returns:
        httpx.AsyncClient: A shared HTTP client
    """
    # Create a unique key for this client configuration
    key = f"{pool_key}:{base_url}"

    if key not in _clients:
        async with _client_lock:
            if key not in _clients:
                logging.info(f"Creating new HTTP client for {key}")
                _clients[key] = httpx.AsyncClient(
                    base_url=base_url.rstrip("/") if base_url else None,
                    headers=headers or {},
                    timeout=httpx.Timeout(timeout),
                    limits=httpx.Limits(
                        max_connections=max_connections,
                        max_keepalive_connections=max_keepalive_connections,
                    ),
                )

    return _clients[key]


async def close_all_clients():
    """Close all HTTP clients in the pool"""
    async with _client_lock:
        for key, client in _clients.items():
            try:
                logging.info(f"Closing HTTP client: {key}")
                await client.aclose()
            except Exception as e:
                logging.error(f"Error closing HTTP client {key}: {str(e)}")

        _clients.clear()


class HttpClient:
    """A reusable HTTP client with connection pooling and error handling"""

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        pool_key: str = "default",
    ):
        """
        Initialize the HTTP client

        Args:
            base_url: Base URL for all requests
            headers: Default headers for all requests
            timeout: Default request timeout in seconds
            pool_key: Identifier for this client pool
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.pool_key = pool_key
        # No client creation - use the pool

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request using the connection pool

        Args:
            path: The endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Dict: JSON response data

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = path.lstrip("/")  # Use relative path with the base_url in the client
        merged_headers = {**self.headers, **(headers or {})}

        logging.info(f"GET request to {self.base_url}/{url}")

        try:
            # Get client from pool
            client = await get_pooled_client(
                self.base_url, self.headers, self.timeout, self.pool_key
            )

            response = await client.get(url, params=params, headers=merged_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP status error: {e.response.status_code} - {str(e)}")
            raise
        except httpx.RequestError as e:
            logging.error(f"Request error: {str(e)}")
            raise

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request using the connection pool

        Args:
            path: The endpoint path
            data: Form data
            json_data: JSON data
            headers: Additional headers

        Returns:
            Dict: JSON response data

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = path.lstrip("/")  # Use relative path with the base_url in the client
        merged_headers = {**self.headers, **(headers or {})}

        # Log request details (excluding sensitive data)
        if json_data:
            log_data = json_data.copy()
            # Redact sensitive fields if present
            for key in ["password", "api_key", "key", "token", "secret"]:
                if key in log_data:
                    log_data[key] = "****"

            # Only log a truncated version of very large payloads
            log_json = json.dumps(log_data)
            if len(log_json) > 1000:
                log_json = log_json[:1000] + "... [truncated]"

            logging.info(
                f"POST request to {self.base_url}/{url} with payload: {log_json}"
            )
        else:
            logging.info(f"POST request to {self.base_url}/{url}")

        try:
            # Get client from pool
            client = await get_pooled_client(
                self.base_url, self.headers, self.timeout, self.pool_key
            )

            response = await client.post(
                url, data=data, json=json_data, headers=merged_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP status error: {e.response.status_code} - {str(e)}")
            raise
        except httpx.RequestError as e:
            logging.error(f"Request error: {str(e)}")
            raise
