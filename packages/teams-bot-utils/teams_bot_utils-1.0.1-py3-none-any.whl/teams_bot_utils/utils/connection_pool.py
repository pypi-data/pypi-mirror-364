"""
Connection pool management for shared HTTP clients
"""

import httpx
import asyncio
from typing import Dict, Optional, Any
from logging import info, error

# Global client instances
_clients: Dict[str, httpx.AsyncClient] = {}
_client_lock = asyncio.Lock()


async def get_http_client(
    base_url: str = "",
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    client_id: str = "default",
    max_connections: int = 100,
    max_keepalive_connections: int = 20,
) -> httpx.AsyncClient:
    """
    Get or create a shared HTTP client with connection pooling

    Args:
        base_url: Base URL for all requests
        headers: Default headers for all requests
        timeout: Default request timeout in seconds
        client_id: Identifier for this client pool
        max_connections: Maximum number of connections
        max_keepalive_connections: Maximum number of idle keepalive connections

    Returns:
        httpx.AsyncClient: A shared HTTP client
    """
    # Create a unique pool key based on the base_url and client_id
    pool_key = f"{client_id}:{base_url}"

    if pool_key not in _clients:
        async with _client_lock:
            if pool_key not in _clients:
                info(f"Creating new shared HTTP client for {pool_key}")
                _clients[pool_key] = httpx.AsyncClient(
                    base_url=base_url.rstrip("/") if base_url else None,
                    headers=headers or {},
                    timeout=httpx.Timeout(timeout),
                    limits=httpx.Limits(
                        max_connections=max_connections,
                        max_keepalive_connections=max_keepalive_connections,
                    ),
                )

    return _clients[pool_key]


async def close_all_clients() -> None:
    """Close all shared HTTP clients"""
    async with _client_lock:
        for key, client in _clients.items():
            try:
                info(f"Closing shared HTTP client: {key}")
                await client.aclose()
            except Exception as e:
                error(f"Error closing HTTP client {key}: {str(e)}")

        _clients.clear()
