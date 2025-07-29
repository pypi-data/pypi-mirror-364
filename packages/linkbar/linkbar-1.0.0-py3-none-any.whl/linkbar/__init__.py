"""
Linkbar Python SDK

A Python client library for the Linkbar API.

Usage:
    import linkbar
    
    linkbar.api_key = "your_api_key"
    link = linkbar.Link.create(long_url="https://example.com", domain="linkb.ar")
    print(f"Created: {link.short_url}")
"""

import requests
from typing import Optional, Dict, Any

# Module-level configuration
api_key: Optional[str] = None
base_url: str = "https://api.linkbar.co/"

def _request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Internal function to make authenticated requests to the Linkbar API.
    """
    if not api_key:
        raise ValueError("API key not set. Set linkbar.api_key = 'your_api_key'")
    
    url = f"{base_url.rstrip('/')}/{endpoint}"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data if method in ['POST', 'PUT', 'PATCH'] else None,
        params=data if method == 'GET' else None
    )
    
    response.raise_for_status()
    return response.json()

from .link import Link
from .domain import Domain

__version__ = "1.0.0"
__all__ = ["api_key", "base_url", "Link", "Domain"]