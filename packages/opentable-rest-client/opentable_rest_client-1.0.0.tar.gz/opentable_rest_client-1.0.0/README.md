# OpenTable REST API Client

A Python client library for the OpenTable REST API. Search restaurants, check availability, book reservations, and manage your dining experiences programmatically.

## Features

- 🔍 **Restaurant Search**: Find restaurants by location and cuisine
- 📅 **Availability Check**: Get real-time availability for any restaurant
- 📝 **Reservation Management**: Book, modify, and cancel reservations
- 💳 **Payment Methods**: Add and manage credit cards
- 👤 **User Management**: Register and authenticate users
- 🔄 **Async Support**: Full async/await support for all operations

## Installation

```bash
pip install opentable-rest-client
```

## Quick Start

### Basic Usage

```python
from opentable_client.client import Client
from opentable_client.models import UserCreate, SearchRequest
from opentable_client.api.production import register_user_production_auth_register_post
from opentable_client.api.default import search_restaurants_search_post

# Initialize client
client = Client(base_url="https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run")

# Register a test user
user_data = UserCreate(
    first_name="John",
    last_name="Doe", 
    phone_number="5551234567"
)

user_response = register_user_production_auth_register_post.sync_detailed(
    client=client,
    body=user_data,
    x_org_key="your-org-key"
)

user = user_response.parsed
print(f"Registered: {user.email}")

# Create authenticated client
auth_client = Client(
    base_url="https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run",
    headers={
        "Authorization": f"Bearer {user.api_token}",
        "X-Org-Key": "your-org-key"
    }
)

# Search for restaurants
search_request = SearchRequest(
    location="New York, NY",
    restaurant_name="italian",
    party_size=2
)

restaurants = search_restaurants_search_post.sync(
    client=auth_client,
    body=search_request,
    x_org_key="your-org-key"
)

print(f"Found {len(restaurants)} restaurants")
```

### Async Usage

```python
import asyncio
from opentable_client.api.default import search_restaurants_search_post

async def search_async():
    restaurants = await search_restaurants_search_post.asyncio(
        client=auth_client,
        body=search_request,
        x_org_key="your-org-key"
    )
    return restaurants

restaurants = asyncio.run(search_async())
```

## API Coverage

This client provides access to all OpenTable REST API endpoints:

### Authentication & Users
- ✅ User registration
- ✅ Token-based authentication

### Restaurant Operations  
- ✅ Restaurant search with filters
- ✅ Get restaurant availability
- ✅ Get detailed restaurant information

### Reservation Management
- ✅ Book reservations
- ✅ List user reservations
- ✅ Modify existing reservations
- ✅ Cancel reservations

### Payment Methods
- ✅ Add credit cards
- ✅ List saved payment methods
- ✅ Handle card-required reservations

## Configuration

The client requires:

1. **Base URL**: The OpenTable API endpoint
2. **Org Key**: Your organization key for API access  
3. **API Token**: User token (obtained via registration)

```python
# Basic client (for registration only)
client = Client(base_url="https://your-api-endpoint.com")

# Authenticated client (for all operations)
auth_client = Client(
    base_url="https://your-api-endpoint.com",
    headers={
        "Authorization": f"Bearer {api_token}",
        "X-Org-Key": "your-org-key"
    }
)
```

## Complete Workflow Example

See [example_usage.py](example_usage.py) for a complete workflow that demonstrates:

1. User registration
2. Restaurant search  
3. Availability checking
4. Credit card management
5. Reservation booking
6. Reservation management

## Error Handling

The client provides detailed error responses:

```python
response = search_restaurants_search_post.sync_detailed(
    client=auth_client,
    body=search_request,
    x_org_key="your-org-key"
)

if response.status_code == 200:
    restaurants = response.parsed
    print(f"Success: {len(restaurants)} restaurants found")
else:
    print(f"Error {response.status_code}: {response.content}")
```

## Contributing

This client is auto-generated from the OpenTable API OpenAPI specification. To update:

1. Get the latest OpenAPI schema
2. Regenerate using `openapi-python-client`
3. Test with the example usage script

## License

MIT License - see LICENSE file for details.

## Support

For API-related issues, refer to the OpenTable API documentation.
For client library issues, please open a GitHub issue.
