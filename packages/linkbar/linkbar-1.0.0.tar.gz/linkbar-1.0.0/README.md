# Linkbar Python SDK

[![Tests](https://github.com/linkbarapp/linkbar-python/actions/workflows/test.yml/badge.svg)](https://github.com/linkbarapp/linkbar-python/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/linkbarapp/linkbar-python/branch/main/graph/badge.svg)](https://codecov.io/gh/linkbarapp/linkbar-python)
[![PyPI version](https://badge.fury.io/py/linkbar.svg)](https://badge.fury.io/py/linkbar)
[![Python versions](https://img.shields.io/pypi/pyversions/linkbar.svg)](https://pypi.org/project/linkbar/)

A Python client library for the Linkbar API that allows you to create, manage, and track short links.

## Installation

```bash
pip install linkbar
```

## Quick Start

```python
import linkbar

# Set your API key
linkbar.api_key = "your_api_key_here"

# Create a short link
link = linkbar.Link.create(long_url="https://example.com", domain="linkb.ar")
print(f"Created: {link.short_url}")
print(f"Redirects to: {link.long_url}")
```

## Authentication

Get your API key from your [Linkbar dashboard](https://linkbar.co/api-settings/) and set it:

```python
import linkbar

linkbar.api_key = "your_api_key_here"
```

You can also configure the base URL if needed (defaults to `https://api.linkbar.co/`):

```python
linkbar.base_url = "https://api.linkbar.co/"
```

## Working with Links

### Creating Links

```python
# Basic link creation
link = linkbar.Link.create(long_url="https://example.com")

# Create with custom domain
link = linkbar.Link.create(
    long_url="https://example.com",
    domain="linkb.ar"
)

# Create with custom keyword
link = linkbar.Link.create(
    long_url="https://example.com",
    domain="linkb.ar",
    keyword="my-link"
)

# Create with tags
link = linkbar.Link.create(
    long_url="https://example.com",
    domain="linkb.ar",
    tags=["marketing", "campaign"]
)
```

### Accessing Link Properties

```python
link = linkbar.Link.create(long_url="https://example.com")

print(f"ID: {link.id}")
print(f"Short URL: {link.short_url}")
print(f"Long URL: {link.long_url}")
print(f"Domain: {link.domain_name}")
print(f"Keyword: {link.keyword}")
print(f"Tags: {link.tags}")
print(f"Click count: {link.click_count}")
print(f"Created at: {link.created_at}")
```

### Managing Links

```python
# List all links
links = linkbar.Link.list()
for link in links:
    print(f"{link.short_url} -> {link.long_url}")

# Search links
marketing_links = linkbar.Link.list(search="marketing")

# Get a specific link
link = linkbar.Link.get(link_id="abc123")

# Update a link
link.update(long_url="https://newexample.com")

# Add tags to an existing link
link.update(tags=["updated", "new-campaign"])

# Delete a link
link.delete()

# Refresh link data from API
link.refresh()
```

## Working with Domains

### Listing Domains

```python
# List all domains (both custom and Linkbar domains)
domains = linkbar.Domain.list()

# List only custom domains
custom_domains = linkbar.Domain.list(is_custom=True)

# Search domains
domains = linkbar.Domain.list(search="example")
```

### Creating Custom Domains

```python
# Create a basic custom domain
domain = linkbar.Domain.create(name="example.com")

# Create domain with redirect URLs
domain = linkbar.Domain.create(
    name="example.com",
    homepage_redirect_url="https://example.com",
    nonexistent_link_redirect_url="https://example.com/404"
)
```

### Managing Domains

```python
# Get a specific domain
domain = linkbar.Domain.get(domain_id="xyz789")

# Access domain properties
print(f"Name: {domain.name}")
print(f"Status: {domain.status}")
print(f"Is custom: {domain.is_custom}")

# Update domain
domain.update(homepage_redirect_url="https://newsite.com")

# Delete domain
domain.delete()

# Refresh domain data
domain.refresh()
```

## Error Handling

```python
import requests
import linkbar

linkbar.api_key = "your_api_key"

try:
    link = linkbar.Link.create(long_url="https://example.com")
    print(f"Created: {link.short_url}")
    
except ValueError as e:
    # API key not set or missing required parameters
    print(f"Configuration error: {e}")
    
except requests.HTTPError as e:
    # API request failed
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 400:
        print(f"Bad request: {e.response.json()}")
    else:
        print(f"API error: {e}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Common Use Cases

### Bulk Link Creation

```python
urls_to_shorten = [
    "https://example.com/page1",
    "https://example.com/page2", 
    "https://example.com/page3"
]

shortened_links = []
for url in urls_to_shorten:
    try:
        link = linkbar.Link.create(long_url=url, domain="linkb.ar")
        shortened_links.append(link)
        print(f"✓ {url} -> {link.short_url}")
    except Exception as e:
        print(f"✗ Failed to shorten {url}: {e}")
```

### Campaign Link Management

```python
# Create campaign links with consistent tagging
campaign_urls = {
    "https://example.com/landing": "landing-page",
    "https://example.com/pricing": "pricing-page",
    "https://example.com/signup": "signup-page"
}

campaign_links = {}
for url, keyword in campaign_urls.items():
    link = linkbar.Link.create(
        long_url=url,
        domain="linkb.ar", 
        keyword=f"summer-{keyword}",
        tags=["summer-campaign", "2024"]
    )
    campaign_links[keyword] = link

# Later, update all campaign links
for link in campaign_links.values():
    link.refresh()  # Get updated click counts
    print(f"{link.keyword}: {link.click_count} clicks")
```

## API Reference

### Link Methods

- `Link.create(long_url, domain=None, keyword=None, tags=None)` - Create a new link
- `Link.list(search=None)` - List links with optional search
- `Link.get(link_id)` - Get a specific link by ID
- `link.update(long_url=None, domain=None, keyword=None, tags=None)` - Update link
- `link.delete()` - Delete link
- `link.refresh()` - Refresh link data from API

### Domain Methods

- `Domain.create(name, homepage_redirect_url=None, nonexistent_link_redirect_url=None)` - Create custom domain
- `Domain.list(search=None, is_custom=None)` - List domains with optional filters
- `Domain.get(domain_id)` - Get a specific domain by ID
- `domain.update(name=None, homepage_redirect_url=None, nonexistent_link_redirect_url=None)` - Update domain
- `domain.delete()` - Delete domain
- `domain.refresh()` - Refresh domain data from API

### Link Properties

- `id` - Unique link identifier
- `short_url` - Full short URL (e.g., "https://linkb.ar/abc123")
- `pretty_url` - Short URL without protocol (e.g., "linkb.ar/abc123")
- `long_url` - Original URL being shortened
- `keyword` - Short link keyword/slug
- `domain` - Domain object or string
- `domain_name` - Domain name as string
- `tags` - List of tags
- `click_count` - Number of clicks (read-only)
- `created_at` - Creation timestamp

### Domain Properties

- `id` - Unique domain identifier
- `name` - Domain name
- `is_custom` - Whether it's a custom domain
- `status` - Domain status (pending, connected, disconnected)
- `organization` - Associated organization
- `homepage_redirect_url` - URL for domain root redirects
- `nonexistent_link_redirect_url` - URL for 404 redirects

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License