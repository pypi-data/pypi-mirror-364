# OpenTable REST API Documentation

## Overview

This API provides programmatic access to OpenTable restaurant reservations, including search, booking, modification, and cancellation capabilities. The API is built with FastAPI and deployed on Modal.

**Base URL**: `https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run`

## Authentication

All endpoints (except health check) require Bearer token authentication. Include your API token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

Tokens are automatically refreshed when they expire, providing seamless authentication.

## Test vs. Production Accounts

⚠️ **Important**: This API supports both test accounts (for development) and real OpenTable accounts (for production use).

### Test Accounts (Created via Registration)
- ✅ **Supported**: Search, availability, booking at restaurants without credit card requirements, list reservations, cancel, modify
- ❌ **Not Supported**: Adding credit cards, booking at restaurants requiring credit cards
- 🎯 **Use Case**: Development, testing, demonstrations

### Real OpenTable Accounts
- ✅ **Fully Supported**: All functionality including credit card management
- 🎯 **Use Case**: Production applications, real reservations

## Endpoints

### 0. Health Check

**Endpoint**: `GET /health`  
**Description**: Check API health status  
**Authentication**: Not required

#### Response (Success - 200)
```json
{
  "status": "healthy",
  "service": "opentable-rest-api"
}
```

---

### 1. User Registration

**Endpoint**: `POST /auth/register`
**Description**: Create a new test OpenTable account with 2FA verification. This endpoint creates a test account suitable for development and testing purposes. The process can take 30-60 seconds due to email-based 2FA.

#### Request Body
```json
{
  "first_name": "Test",
  "last_name": "User", 
  "phone_number": "5551234567"
}
```

#### Parameters
- `first_name` (required): User's first name
- `last_name` (required): User's last name  
- `phone_number` (required): 10-digit US phone number without country code

#### Response (Success - 200)
```json
{
  "user_id": "a9942657-cce2-43fb-8088-951555b039ea",
  "api_token": "3cde42d7-8641-4fac-ba2f-76e01af4f4bf",
  "email": "dojarob+ot3a449f37@gmail.com",
  "first_name": "Test",
  "last_name": "User",
  "phone_number": "5551234567",
  "created_at": "2025-07-24T01:05:01.792105+00:00"
}
```

#### Error Response (422 - Missing Fields)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "last_name"],
      "msg": "Field required",
      "input": {"first_name": "Test"}
    },
    {
      "type": "missing", 
      "loc": ["body", "phone_number"],
      "msg": "Field required",
      "input": {"first_name": "Test"}
    }
  ]
}
```

---

### 2. Restaurant Search

**Endpoint**: `POST /search`  
**Description**: Search for restaurants by location and optional filters. Returns comprehensive restaurant data including ratings, price bands, and next available times.

#### Request Body
```json
{
  "location": "New York, NY",
  "restaurant_name": "italian",
  "party_size": 2,
  "max_results": 20
}
```

#### Parameters
- `location` (required): City, address, or landmark for geocoding
- `restaurant_name` (optional): Restaurant name, cuisine type, or search term  
- `party_size` (optional, default: 2): Number of diners
- `max_results` (optional): Maximum restaurants to return ⚠️ **Note**: Currently ignored, always returns 50 results

#### Response (Success - 200)
```json
{
  "restaurants": [
    {
      "id": "212347",
      "name": "SAN CARLO  Osteria Piemonte",
      "city": "New York",
      "region": "NA",
      "rating": 4.8,
      "price_band": "$31 to $50",
      "cuisines": ["Italian"],
      "num_booked": null,
      "next_available_time": "12:00 PM Local",
      "next_available_party_size": 2,
      "timezone": "Local",
      "utc_offset": 0
    }
  ],
  "search_location": {
    "latitude": 40.7127281,
    "longitude": -74.0060152
  },
  "total_results": 50,
  "user_id": "a9942657-cce2-43fb-8088-951555b039ea",
  "search_params": {
    "location": "New York, NY",
    "restaurant_name": "italian",
    "date_time": null,
    "party_size": 2,
    "max_results": 20
  }
}
```

#### Error Response (401 - Not Authenticated)
```json
{
  "detail": "Not authenticated"
}
```

#### Error Response (422 - Missing Location)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "location"],
      "msg": "Field required",
      "input": {"restaurant_name": "italian"}
    }
  ]
}
```

---

### 3. Restaurant Availability

**Endpoint**: `GET /availability/{restaurant_id}`  
**Description**: Get available time slots for a specific restaurant with detailed slot information including credit card requirements.

#### Path Parameters
- `restaurant_id` (required): Restaurant ID from search results

#### Query Parameters
- `party_size` (optional, default: 2): Number of diners
- `days` (optional, default: 7): Days to scan ahead  
- `start_hour` (optional, default: 17): Earliest hour (24h format)
- `end_hour` (optional, default: 21): Latest hour (24h format)

#### Example Request
```bash
GET /availability/30196?party_size=2&days=1
```

#### Response (Success - 200)
```json
{
  "restaurant_id": 30196,
  "party_size": 2,
  "scan_parameters": {
    "start_date": "2025-07-24",
    "days_scanned": 1,
    "start_hour": 17,
    "end_hour": 21
  },
  "raw_api_responses": [
    {
      "query_datetime": "2025-07-24T17:00:00",
      "response": {
        "availability": {
          "dateTime": "2025-07-24T17:00",
          "id": "30196",
          "timeslots": [
            {
              "dateTime": "2025-07-24T17:00",
              "available": true,
              "requiresCreditCard": true,
              "slotHash": "2431185583",
              "token": "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ",
              "points": 100,
              "type": "Standard",
              "priceAmount": 0,
              "creditCardPolicyType": "HOLD"
            }
          ],
          "availabilityToken": "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ"
        }
      }
    }
  ],
  "user_id": "a9942657-cce2-43fb-8088-951555b039ea",
  "request_params": {
    "restaurant_id": 30196,
    "party_size": 2,
    "days": 1,
    "start_hour": 17,
    "end_hour": 21,
    "start_date": null
  }
}
```

#### Key Response Fields
- `timeslots[].dateTime`: ISO datetime of the slot
- `timeslots[].slotHash`: Required for booking
- `timeslots[].token`: Required for booking  
- `timeslots[].requiresCreditCard`: Whether this slot requires a credit card
- `timeslots[].creditCardPolicyType`: Type of credit card policy ("HOLD", etc.)
- `availabilityToken`: Required for booking

#### Error Response (Invalid Restaurant)
Returns empty `raw_api_responses` array for non-existent restaurant IDs, not an error.

---

### 4. Add Credit Card

**Endpoint**: `POST /cards`  
**Description**: Add a credit card to your OpenTable account for reservations requiring credit card holds. 

⚠️ **Important**: This endpoint only works with real OpenTable accounts, not test accounts created via registration.

#### Request Body
```json
{
  "card_full_name": "John Doe",
  "card_number": "4111111111111111",
  "card_exp_month": 12,
  "card_exp_year": 2025,
  "card_cvv": "123",
  "card_zip": "10001"
}
```

#### Parameters
- `card_full_name` (required): Full name as it appears on the card
- `card_number` (required): Credit card number (will be tokenized securely)
- `card_exp_month` (required): Expiration month (1-12)
- `card_exp_year` (required): Expiration year (YYYY)  
- `card_cvv` (required): Card verification value (3-4 digits)
- `card_zip` (required): Billing ZIP code

#### Response (Success - 200)
```json
{
  "status": "success",
  "message": "Credit card added successfully",
  "card": {
    "id": "9b44036b-226a-499b-8eda-9b488fc9e197",
    "type": "Visa",
    "last4": "1111", 
    "expiry_month": "12",
    "expiry_year": "25",
    "default": true
  }
}
```

#### Error Response (Test Account - 422)
```json
{
  "detail": "Failed to communicate with OpenTable: Failed to add card: 404 - {\"error\":{\"code\":\"UNKNOWN\",\"shouldRetokenize\":false}}"
}
```

#### Error Response (Missing Fields - 422)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "card_exp_month"],
      "msg": "Field required",
      "input": {"card_full_name": "Test User", "card_number": "4111111111111111"}
    }
  ]
}
```

---

### 5. List Saved Cards

**Endpoint**: `GET /cards`  
**Description**: List all credit cards saved to your OpenTable account

#### Response (Success - 200)
```json
{
  "user_id": "a9942657-cce2-43fb-8088-951555b039ea",
  "cards": [],
  "total_cards": 0
}
```

**Note**: Test accounts will always return an empty cards array.

---

### 6. Book Reservation

**Endpoint**: `POST /book`  
**Description**: Book a restaurant reservation. Use data from the availability endpoint to construct the booking request.

#### Request Body
```json
{
  "restaurant_id": 212347,
  "slot_hash": "1970015633",
  "date_time": "2025-07-24T13:30",
  "availability_token": "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ",
  "party_size": 2,
  "location": "New York, NY",
  "table_attribute": "default",
  "special_requests": "Window table preferred",
  "occasion": "birthday",
  "sms_opt_in": true
}
```

#### Parameters
- `restaurant_id` (required): Restaurant ID from search results
- `slot_hash` (required): Slot hash from availability response
- `date_time` (required): Reservation datetime (YYYY-MM-DDTHH:MM)
- `availability_token` (required): Token from availability response
- `party_size` (required): Number of diners
- `location` (required): Location for geocoding  
- `table_attribute` (optional, default: "default"): Seating preference
- `special_requests` (optional): Special requests or notes
- `occasion` (optional): Occasion type ("birthday", "anniversary", etc.)
- `sms_opt_in` (optional, default: true): SMS notification preferences

#### Response (Success - 201)
```json
{
  "status": "success",
  "message": "Reservation booked successfully",
  "reservation": {
    "confirmationNumber": "101750",
    "token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1",
    "restaurant": {
      "id": "212347",
      "name": "SAN CARLO  Osteria Piemonte"
    },
    "dateTime": "2025-07-24T13:30",
    "partySize": 2,
    "status": 1,
    "reservationStatus": "Pending",
    "creditCard": false
  },
  "lock_id": "1879966478"
}
```

#### Error Response (Credit Card Required)
For restaurants requiring credit cards:
```json
{
  "detail": "Credit card is required for this reservation. Please add a card to your account using the POST /cards endpoint first."
}
```

---

### 7. List User Reservations

**Endpoint**: `GET /reservations`  
**Description**: Get comprehensive user profile and reservation history

#### Response (Success - 200)
```json
{
  "globalPersonId": "150238676545",
  "customerId": "263863380",
  "firstName": "Test",
  "lastName": "User",
  "email": "dojarob+ot3a449f37@gmail.com",
  "reservations": {
    "history": [
      {
        "confirmationNumber": "101750",
        "token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1",
        "restaurant": {
          "id": "212347",
          "name": "SAN CARLO  Osteria Piemonte"
        },
        "dateTime": "2025-07-24T13:30",
        "partySize": 2,
        "status": 1,
        "reservationStatus": "Pending",
        "creditCard": false
      }
    ],
    "totalCount": 1
  },
  "statistics": {
    "reservationsCount": 1,
    "reviewsCount": 0,
    "photosCount": 0
  },
  "wallet": {
    "maxCards": 5,
    "cards": []
  }
}
```

---

### 8. Cancel Reservation

**Endpoint**: `DELETE /reservations/{confirmation_number}`  
**Description**: Cancel an existing reservation

#### Path Parameters
- `confirmation_number` (required): Reservation confirmation number

#### Request Body
```json
{
  "restaurant_id": "212347",
  "reservation_token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1"
}
```

#### Parameters
- `restaurant_id` (required): Restaurant ID from the reservation
- `reservation_token` (required): Token from the reservation object

#### Response (Success - 200)
```json
{
  "success": true,
  "user_id": "a9942657-cce2-43fb-8088-951555b039ea",
  "confirmation_number": "101750",
  "message": "Reservation successfully cancelled."
}
```

---

### 9. Modify Reservation

**Endpoint**: `PUT /reservations/{confirmation_number}/modify`  
**Description**: Modify an existing reservation by moving it to a new available slot

#### Path Parameters
- `confirmation_number` (required): Reservation confirmation number

#### Request Body
```json
{
  "reservation_token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1",
  "restaurant_id": 212347,
  "new_slot_hash": "4122579851",
  "new_date_time": "2025-07-27T21:00",
  "new_availability_token": "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ",
  "party_size": 2,
  "special_requests": "Window table preferred",
  "occasion": "anniversary",
  "phone_number": "5551234567",
  "seating_preference": "default"
}
```

#### Required Parameters
- `reservation_token` (required): Token from the original reservation
- `restaurant_id` (required): Restaurant ID
- `new_slot_hash` (required): Slot hash from availability endpoint
- `new_date_time` (required): New reservation datetime
- `new_availability_token` (required): Availability token from availability endpoint

#### Optional Parameters  
- `party_size` (optional): New party size
- `special_requests` (optional): Special requests
- `occasion` (optional): Occasion type
- `phone_number` (optional): Phone number
- `seating_preference` (optional): Seating preference

#### Error Response (Missing Fields - 422)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "new_slot_hash"],
      "msg": "Field required", 
      "input": {"reservation_token": "invalid_token"}
    },
    {
      "type": "missing",
      "loc": ["body", "new_date_time"],
      "msg": "Field required",
      "input": {"reservation_token": "invalid_token"}
    },
    {
      "type": "missing",
      "loc": ["body", "new_availability_token"],
      "msg": "Field required",
      "input": {"reservation_token": "invalid_token"}
    },
    {
      "type": "missing",
      "loc": ["body", "restaurant_id"],
      "msg": "Field required",
      "input": {"reservation_token": "invalid_token"}
    }
  ]
}
```

---

## Complete Workflow Examples

### 1. Development/Testing Flow (Test Accounts)
```bash
# 1. Create test account
curl -X POST "/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Test", "last_name": "User", "phone_number": "5551234567"}'
# Save the api_token from response

# 2. Search for restaurants  
curl -X POST "/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "New York, NY", "restaurant_name": "italian"}'

# 3. Check availability
curl -X GET "/availability/212347?party_size=2&days=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Book reservation (restaurants not requiring credit cards only)
curl -X POST "/book" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 212347,
    "slot_hash": "1970015633", 
    "date_time": "2025-07-24T13:30",
    "availability_token": "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ",
    "party_size": 2,
    "location": "New York, NY"
  }'

# 5. List reservations
curl -X GET "/reservations" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Cancel reservation
curl -X DELETE "/reservations/101750" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": "212347", "reservation_token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1"}'
```

### 2. Production Flow (Real Accounts)
For production use with real OpenTable accounts, all endpoints work including credit card management for restaurants requiring card holds.

---

## Error Handling

### Authentication Errors
```json
// 401 Unauthorized
{"detail": "Not authenticated"}
```

### Validation Errors
```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

### Business Logic Errors  
```json
// 422 Unprocessable Entity
{"detail": "Specific error message describing the issue"}
```

---

## Data Formats

### Date/Time Format
- All datetime fields use ISO 8601 format: `YYYY-MM-DDTHH:MM`
- Times are in local restaurant timezone
- Example: `2025-07-24T13:30`

### Phone Numbers
- US format: 10 digits without country code
- Example: `5551234567`

### Location Format
- Free-form text that gets geocoded
- Examples: "New York, NY", "123 Main St, Boston, MA", "Times Square"

---

## Rate Limiting

- No explicit rate limits currently implemented
- OpenTable's underlying API may have its own rate limits
- Recommended: Max 10 requests per minute per user

---

## Notes & Limitations

### Test Account Limitations
- ❌ Cannot add credit cards
- ❌ Cannot book at restaurants requiring credit cards  
- ✅ Can book at restaurants without credit card requirements
- ✅ Full reservation management (list, cancel, modify)

### Known Issues
- `max_results` parameter in search is currently ignored
- Availability response structure is more complex than originally documented

### Credit Card Integration
- Uses Spreedly for secure tokenization
- Cards are stored in your actual OpenTable account
- Required for high-end restaurants and certain time slots

---

## Python Client (Auto-Generated)

A comprehensive, auto-generated Python client is available in the `python_client/` folder. This client is generated directly from the API's OpenAPI schema, ensuring it's always up-to-date with the server implementation.

### Features
- ✅ **Always In Sync**: Generated from `openapi.json` for perfect server alignment
- 🛡️ **Type-Safe**: Complete type hints for better IDE support
- 🚀 **Modern**: Uses `httpx` with support for async operations
- 📦 **Fully Packaged**: Includes `pyproject.toml` for easy installation

### Getting Started

1.  **Install the client**:
    ```bash
    cd python_client/
    pip install .
    ```

2.  **Use in your code**:
    ```python
    from open_table_rest_api_client.api.production import register_user_production_auth_register_post
    from open_table_rest_api_client.models import UserCreate, UserPublic
    from open_table_rest_api_client.client import Client

    # Initialize the client
    client = Client(base_url="https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run")

    # Register a new user
    user_data = UserCreate(
        first_name="Test",
        last_name="User",
        phone_number="5551234567"
    )
    user: UserPublic = register_user_production_auth_register_post.sync(
        client=client,
        body=user_data
    )

    print(f"Registered user: {user.email}")
    print(f"API Token: {user.api_token}")
    ```

### How to Regenerate the Client
If you make changes to the API in `api/main.py`, you can easily regenerate the client:

1.  **Get the latest OpenAPI schema**:
    ```bash
    curl https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run/openapi.json > python_client/openapi.json
    ```

2.  **Regenerate the client**:
    ```bash
    openapi-python-client generate --path python_client/openapi.json --output-path python_client/
    ```

See `python_client/README.md` for complete, auto-generated documentation on all available methods and models.

---

## Support

For issues or questions:
- Check error messages for specific guidance
- Ensure all required fields are provided  
- Verify authentication token is valid
- Use test accounts for development/testing
- Use real OpenTable accounts for production reservations
- Contact support if problems persist

---

## Changelog

### v1.2.0 (Current)
- ✅ Comprehensive testing completed on all endpoints
- ✅ Updated documentation with accurate response formats
- ✅ Added test vs. production account guidance
- ✅ Fixed availability response structure documentation
- ✅ Added comprehensive error response examples
- ✅ Added complete workflow examples for both test and production use

### v1.1.0
- Updated modify reservation to use direct slot specification
- Added comprehensive error handling for business rule limitations
- Enhanced documentation with complete workflow examples
- Fixed credit card integration for modify operations

### v1.0.0
- Initial API release
- All core reservation management features
- Automatic token refresh
- Comprehensive error handling
- Test account support for development 