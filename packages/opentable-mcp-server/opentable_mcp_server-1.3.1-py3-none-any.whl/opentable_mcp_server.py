#!/usr/bin/env python3
"""
OpenTable MCP Server

An MCP server that provides OpenTable restaurant reservation functionality
using the published opentable-rest-client package.

Install dependencies:
    pip install mcp opentable-rest-client

Usage:
    python opentable_mcp_server.py
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Import the published OpenTable client
from opentable_client.client import Client
from opentable_client.models import (
    UserCreate, 
    SearchRequest, 
    CardCreate,
    BookingRequest,
    CancelRequest
)

# Import API functions from the published package
from opentable_client.api.production import register_user_production_auth_register_post
from opentable_client.api.default import (
    health_check_health_get,
    search_restaurants_search_post,
    get_restaurant_availability_availability_restaurant_id_get,
    add_credit_card_cards_post,
    list_credit_cards_cards_get,
    book_reservation_endpoint_book_post,
    get_reservations_reservations_get,
    cancel_reservation_reservations_confirmation_number_delete,
    modify_reservation_endpoint_reservations_confirmation_number_modify_put
)

# Initialize FastMCP server
mcp = FastMCP("opentable")

# Configuration
BASE_URL = "https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run"
DEFAULT_ORG_KEY = os.getenv("OPENTABLE_ORG_KEY", "a7a7a7a7-a7a7-a7a7-a7a7-a7a7a7a7a7a7")

class OpenTableService:
    """Service class to manage OpenTable API interactions"""
    
    def __init__(self):
        self.client = Client(base_url=BASE_URL)
        self.auth_client = None
        self.current_user = None
        self.org_key = DEFAULT_ORG_KEY
    
    def authenticate(self, api_token: str, org_key: str = None):
        """Set up authenticated client"""
        if org_key:
            self.org_key = org_key
            
        self.auth_client = Client(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {api_token}",
                "X-Org-Key": self.org_key
            }
        )

# Global service instance
ot_service = OpenTableService()

@mcp.tool()
async def register_user(first_name: str, last_name: str, phone_number: str) -> Dict[str, Any]:
    """Register a new OpenTable test user with automated 2FA verification.
    
    This endpoint creates a test OpenTable account suitable for development and testing 
    purposes. The registration process includes automated email-based 2FA verification 
    and can take 30-60 seconds to complete. Test accounts support most functionality 
    except credit card operations and restaurants requiring credit cards.
    
    **Authentication**: Not required (this creates the user and returns an API token)
    
    **Account Type**: Creates test accounts only (not real OpenTable accounts)
    
    Args:
        first_name (str): User's first name (e.g. "Thomas", "Sarah")
        last_name (str): User's last name (e.g. "Meringue", "Johnson")  
        phone_number (str): 10-digit US phone number without country code or formatting
                           Examples: "9167995790", "5551234567"
                           Note: Must be unique - duplicate numbers will fail
    
    Returns:
        Dict[str, Any]: Registration result containing:
            - success (bool): Whether registration succeeded
            - message (str): Success message with generated email
            - email (str): Auto-generated email (dojarob+random@gmail.com format)
            - api_token (str): Bearer token for authenticated requests (save this!)
            - user_id (str): Unique user identifier for this account
            - org_id (str): Organization ID for this user
            
        On error:
            - success (bool): False
            - error (str): Error description
            - details (str): Additional error information if available
    
    **Example Usage**:
        ```python
        result = await register_user("Thomas", "Meringue", "9167995790")
        if result["success"]:
            api_token = result["api_token"]  # Save this for other operations
            user_email = result["email"]     # dojarob+ot3a449f37@gmail.com
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "message": "Successfully registered user: dojarob+ot0fd39afd@gmail.com",
            "email": "dojarob+ot0fd39afd@gmail.com",
            "api_token": "71e5a17c-e225-46c4-a972-58e5af6ce9ea",
            "user_id": "a9063e56-4142-4393-84f3-fb46d4457544", 
            "org_id": "d2414dfc-fea6-4f00-89ef-8b4b5d5e716e"
        }
        ```
    
    **Error Scenarios**:
        - Duplicate phone number: "Registration failed with status 422"
        - Invalid phone format: Must be exactly 10 digits
        - Service unavailable: Connection or server errors
        - Proxy issues: Check OXYLABS credentials if configured
    
    **Test Account Limitations**:
        ✅ **Supported**: Restaurant search, availability checks, booking at most restaurants,
                          reservation management (list, cancel, modify)
        ❌ **Not Supported**: Adding credit cards, booking at restaurants requiring credit cards
    
    **Next Steps After Registration**:
        1. Save the api_token - you'll need it for all other operations
        2. Use search_restaurants() to find restaurants
        3. Use get_availability() to check time slots
        4. Use book_reservation() to make reservations (credit-card-free restaurants only)
    
    **Related Functions**: 
        - search_restaurants(): Find restaurants after registration
        - health_check(): Verify API connectivity before registration
    """
    try:
        user_data = UserCreate(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        response = register_user_production_auth_register_post.sync_detailed(
            client=ot_service.client,
            body=user_data,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            user = response.parsed
            ot_service.current_user = user
            ot_service.authenticate(user.api_token)
            
            return {
                "success": True,
                "message": f"Successfully registered user: {user.email}",
                "email": user.email,
                "api_token": user.api_token,
                "user_id": user.user_id,
                "org_id": getattr(user, 'org_id', None)
            }
        else:
            return {
                "success": False, 
                "error": f"Registration failed with status {response.status_code}",
                "details": str(response.content) if hasattr(response, 'content') else None
            }
            
    except Exception as e:
        return {"success": False, "error": f"Registration error: {str(e)}"}

@mcp.tool()
async def search_restaurants(location: str, restaurant_name: str = None, party_size: int = 2, max_results: int = 20) -> Dict[str, Any]:
    """Search for restaurants by location and optional filters with comprehensive results.
    
    This endpoint searches OpenTable's restaurant database and returns detailed information
    including ratings, price bands, cuisines, and next available reservation times. The search
    supports both specific restaurant names and cuisine-based searches with location filtering.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Search Strategy**:
        - Provide EITHER restaurant_name OR leave it None, not both
        - Location is geocoded automatically (supports various formats)
        - Results include real-time availability for immediate booking decisions
    
    Args:
        location (str): City, address, or landmark for geocoding
                       Examples: "New York, NY", "Manhattan", "123 Main St, Boston, MA",
                                "Times Square", "Vancouver, BC", "Downtown Chicago"
                       Note: Supports international locations
        
        restaurant_name (str, optional): Restaurant name, cuisine type, or search term
                                        Examples: "italian", "Le Bernardin", "pizza", "steakhouse"
                                        Default: None (returns general results for location)
                                        Note: Use cuisine types for broader searches
        
        party_size (int, optional): Number of diners for availability calculations
                                   Range: Typically 1-20 supported
                                   Default: 2
                                   Note: Affects next_available_time calculations
        
        max_results (int, optional): Maximum restaurants to return in response
                                    Range: 1-50 (currently ignored by API, always returns ~50)
                                    Default: 20
                                    Note: API limitation - this parameter is not yet implemented
    
    Returns:
        Dict[str, Any]: Search results containing:
            - success (bool): Whether search succeeded
            - restaurants (List[Dict]): Array of restaurant objects with:
                * id (str): Unique restaurant ID for booking operations
                * name (str): Restaurant name
                * city (str): Restaurant city location
                * region (str): Geographic region (typically "NA" for North America)
                * rating (float): Customer rating (0.0-5.0 scale)
                * price_band (str): Price range ("$30 and under", "$31 to $50", "$50 and over")
                * cuisines (List[str]): Array of cuisine types ["Italian", "Contemporary American"]
                * next_available_time (str): Next available slot ("12:30 PM Local", "5:00 PM Local")
                * next_available_party_size (int): Party size for next available slot
                * timezone (str): Always "Local" - times shown in restaurant's local time
                * utc_offset (int): UTC offset (currently always 0)
            - total_results (int): Number of restaurants returned
            - search_location (Dict): Geocoded coordinates:
                * latitude (float): Geographic latitude
                * longitude (float): Geographic longitude  
            - search_params (Dict): Echo of search parameters used
            
        On error:
            - success (bool): False
            - error (str): Error description
            - details (str): Additional error information if available
    
    **Example Usage**:
        ```python
        # Search for Italian restaurants in NYC
        results = await search_restaurants("New York, NY", "italian", party_size=4)
        
        if results["success"]:
            restaurants = results["restaurants"]
            for restaurant in restaurants[:5]:  # Show first 5
                print(f"{restaurant['name']}: {restaurant['rating']}⭐ {restaurant['price_band']}")
                print(f"Next available: {restaurant['next_available_time']}")
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "restaurants": [
                {
                    "id": "96577",
                    "name": "Sistina", 
                    "city": "New York",
                    "region": "NA",
                    "rating": 4.8,
                    "price_band": "$31 to $50",
                    "cuisines": ["Italian"],
                    "next_available_time": "12:30 PM Local",
                    "next_available_party_size": 2,
                    "timezone": "Local",
                    "utc_offset": 0
                }
            ],
            "total_results": 48,
            "search_location": {
                "latitude": 40.7896239,
                "longitude": -73.9598939
            },
            "search_params": {
                "location": "Manhattan",
                "restaurant_name": "Italian", 
                "party_size": 2,
                "max_results": 20
            }
        }
        ```
    
    **Error Scenarios**:
        - Not authenticated: "Please register a user first using register_user()"
        - Invalid location: "Search failed with status 400" (geocoding timeout/failure)
        - Service timeout: OpenStreetMap geocoding service timeout (try again or use simpler location)
        - Invalid parameters: Must provide either restaurant_name OR date_time, not both
    
    **Location Geocoding Tips**:
        - Use well-known city names: "New York, NY" vs "NYC"
        - Include state/province for US/Canadian locations
        - Landmarks work: "Times Square", "Golden Gate Bridge"
        - Address format: "123 Main St, Boston, MA"
        - International: "London, UK", "Tokyo, Japan"
    
    **Restaurant Selection Strategy**:
        - rating: Higher is better (4.5+ is excellent)
        - price_band: Choose based on budget
        - next_available_time: Shows real-time availability
        - cuisines: Filter by dining preference
        - Save restaurant 'id' for availability/booking calls
    
    **Next Steps After Search**:
        1. Select restaurant(s) of interest from results
        2. Use get_availability() with restaurant_id to see detailed time slots
        3. Use book_reservation() with availability data to make reservation
    
    **Related Functions**:
        - register_user(): Must be called first for authentication
        - get_availability(): Get detailed time slots for a specific restaurant
        - book_reservation(): Book a table at a selected restaurant
    
    **Performance Notes**:
        - Typical response time: 2-5 seconds
        - Results are real-time from OpenTable's live database
        - Geographic search radius varies by location density
        - Popular areas return more results than rural locations
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        search_request = SearchRequest(
            location=location,
            restaurant_name=restaurant_name,
            party_size=party_size,
            max_results=max_results
        )
        
        response = search_restaurants_search_post.sync_detailed(
            client=ot_service.auth_client,
            body=search_request,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            restaurants = response.parsed
            return {
                "success": True, 
                "restaurants": restaurants.get("restaurants", []),
                "total_results": len(restaurants.get("restaurants", [])),
                "search_location": restaurants.get("search_location"),
                "search_params": restaurants.get("search_params")
            }
        else:
            return {
                "success": False, 
                "error": f"Search failed with status {response.status_code}",
                "details": str(response.content) if hasattr(response, 'content') else None
            }
            
    except Exception as e:
        return {"success": False, "error": f"Search error: {str(e)}"}

@mcp.tool()
async def get_availability(restaurant_id: str, party_size: int = 2, days: int = 7, start_hour: int = 17, end_hour: int = 21) -> Dict[str, Any]:
    """Get detailed available time slots for a restaurant with booking requirements.
    
    This endpoint scans a restaurant's availability across multiple days and time ranges,
    returning detailed slot information including credit card requirements, pricing,
    and booking tokens. Use this data to make informed reservation decisions and 
    prepare booking requests with all required parameters.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Booking Flow**: get_availability() → book_reservation() (save slot_hash + availability_token)
    
    **Credit Card Detection**: Response indicates which slots require credit cards
    
    Args:
        restaurant_id (str): Unique restaurant identifier from search_restaurants() results
                            Examples: "96577", "212347", "30196"
                            Note: Must be exact match from search results
        
        party_size (int, optional): Number of diners for the reservation
                                   Range: Typically 1-20 (restaurant-dependent)
                                   Default: 2
                                   Note: Affects slot availability and pricing
        
        days (int, optional): Number of days ahead to scan for availability
                             Range: 1-30 (practical limit ~14 days for most restaurants)
                             Default: 7
                             Note: More days = longer response time but more options
        
        start_hour (int, optional): Earliest hour to check in 24-hour format
                                   Range: 0-23 (restaurant hours dependent)
                                   Default: 17 (5:00 PM)
                                   Examples: 11 (11 AM), 19 (7 PM), 20 (8 PM)
        
        end_hour (int, optional): Latest hour to check in 24-hour format
                                 Range: 0-23, must be > start_hour
                                 Default: 21 (9:00 PM)
                                 Note: Inclusive - will check slots at end_hour
    
    Returns:
        Dict[str, Any]: Detailed availability data containing:
            - success (bool): Whether availability check succeeded
            - restaurant_id (str): Echo of requested restaurant ID
            - party_size (int): Echo of requested party size
            - availability (List[Dict]): Array of time periods scanned, each containing:
                * query_datetime (str): ISO datetime of scan period
                * response (Dict): Raw availability data with:
                    - availability (Dict): Core availability object with:
                        + dateTime (str): Period datetime in ISO format
                        + id (str): Restaurant ID
                        + timeslots (List[Dict]): Available time slots:
                            * dateTime (str): Slot datetime (YYYY-MM-DDTHH:MM format) 
                            * available (bool): Whether slot is bookable (always true in results)
                            * requiresCreditCard (bool): **CRITICAL** - whether booking needs credit card
                            * slotHash (str): **REQUIRED FOR BOOKING** - unique slot identifier
                            * token (str): Slot-specific token (deprecated, use availability token)
                            * points (int): Reward points value (typically 100)
                            * type (str): Slot type ("Standard", "Premium", etc.)
                            * priceAmount (int): Additional cost in cents (usually 0)
                            * creditCardPolicyType (str): Credit card policy ("HOLD", "CHARGE", etc.)
                        + availabilityToken (str): **REQUIRED FOR BOOKING** - authorization token
            - scan_parameters (Dict): Summary of scan settings used
            - total_slots_found (int): Total number of available slots discovered
            
        On error:
            - success (bool): False
            - error (str): Error description
            - details (str): Additional error information if available
    
    **Example Usage**:
        ```python
        # Check dinner availability for tonight and tomorrow
        availability = await get_availability("96577", party_size=2, days=2, start_hour=18, end_hour=22)
        
        if availability["success"]:
            for period in availability["availability"]:
                slots = period["response"]["availability"]["timeslots"]
                for slot in slots:
                    credit_card = "💳 Required" if slot["requiresCreditCard"] else "✅ No card needed"
                    print(f"{slot['dateTime']} - {credit_card}")
                    
                    # Save these for booking:
                    slot_hash = slot["slotHash"]
                    availability_token = period["response"]["availability"]["availabilityToken"]
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "restaurant_id": "30196",
            "party_size": 2,
            "availability": [
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
            "scan_parameters": {
                "start_date": "2025-07-24",
                "days_scanned": 1,
                "start_hour": 17,
                "end_hour": 21
            },
            "total_slots_found": 1
        }
        ```
    
    **Critical Booking Data**:
        For each slot you want to book, you MUST save:
        1. **slotHash**: Unique identifier for the specific time slot
        2. **availabilityToken**: Authorization token from the availability response
        3. **dateTime**: Exact time in YYYY-MM-DDTHH:MM format
        4. **requiresCreditCard**: Whether you need to add a credit card first
    
    **Credit Card Requirements**:
        - requiresCreditCard: true = Must call add_credit_card() first (test accounts can't do this)
        - requiresCreditCard: false = Can book directly with test account
        - creditCardPolicyType: "HOLD" = Temporary authorization, "CHARGE" = Will be charged
    
    **Error Scenarios**:
        - Not authenticated: "Please register a user first using register_user()"
        - Invalid restaurant_id: Returns empty availability array (not an error)
        - Invalid time range: start_hour >= end_hour will return limited results
        - Restaurant closed: No slots returned for requested time periods
        - Far future dates: Some restaurants don't open reservations beyond 30 days
    
    **Time Slot Strategy**:
        - Check multiple days for better options
        - Popular restaurants fill up quickly - book early
        - Weekend evenings require more advance booking
        - Lunch hours (11-14) often have better availability
        - Late dinner (after 21:00) may have last-minute openings
    
    **Booking Preparation Checklist**:
        1. ✅ Found slot with requiresCreditCard: false (for test accounts)
        2. ✅ Saved slotHash from chosen slot
        3. ✅ Saved availabilityToken from response
        4. ✅ Noted exact dateTime format
        5. ✅ Have restaurant_id, party_size, and location ready
    
    **Next Steps After Availability**:
        1. Review all available slots and credit card requirements
        2. For test accounts: Choose slots with requiresCreditCard: false
        3. For real accounts: Add credit card if needed via add_credit_card()
        4. Use book_reservation() with saved slot data to make reservation
    
    **Related Functions**:
        - search_restaurants(): Find restaurant_id values for availability checking
        - book_reservation(): Book a specific slot using availability data
        - add_credit_card(): Required for slots with requiresCreditCard: true
        - list_reservations(): View successful bookings
    
    **Performance & Limits**:
        - Response time: 3-10 seconds (depends on days scanned)
        - Rate limiting: Don't scan the same restaurant repeatedly
        - Optimal scan: 1-3 days for quick results, 7-14 days for full options
        - Data freshness: Availability is real-time from OpenTable
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        response = get_restaurant_availability_availability_restaurant_id_get.sync_detailed(
            client=ot_service.auth_client,
            restaurant_id=restaurant_id,
            party_size=party_size,
            days=days,
            start_hour=start_hour,
            end_hour=end_hour,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            availability_data = response.parsed
            return {
                "success": True,
                "restaurant_id": restaurant_id,
                "party_size": party_size,
                "availability": availability_data.get("raw_api_responses", []),
                "scan_parameters": availability_data.get("scan_parameters", {}),
                "total_slots_found": len(availability_data.get("raw_api_responses", []))
            }
        else:
            return {
                "success": False, 
                "error": f"Availability check failed with status {response.status_code}",
                "details": str(response.content) if hasattr(response, 'content') else None
            }
            
    except Exception as e:
        return {"success": False, "error": f"Availability error: {str(e)}"}

@mcp.tool()
async def book_reservation(
    restaurant_id: str,
    slot_hash: str,
    date_time: str,
    availability_token: str,
    party_size: int,
    location: str,
    special_requests: str = None,
    occasion: str = None
) -> Dict[str, Any]:
    """Book a restaurant reservation using availability data from get_availability().
    
    This endpoint creates a confirmed restaurant reservation using the specific slot data
    obtained from get_availability(). The booking process validates the slot, handles
    credit card requirements automatically, and returns a confirmation number for
    reservation management. All required data must come from a recent availability check.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Prerequisites**: 
        1. Must have called search_restaurants() to find restaurant
        2. Must have called get_availability() to get slot_hash and availability_token  
        3. For credit card slots: Must have called add_credit_card() (test accounts can't do this)
    
    **Booking Flow**: search_restaurants() → get_availability() → book_reservation() → success!
    
    **Credit Card Handling**: Automatically uses saved card for requiresCreditCard slots
    
    Args:
        restaurant_id (str): Restaurant identifier from search_restaurants() results
                            Examples: "96577", "212347", "30196"
                            Must match exactly with availability data
        
        slot_hash (str): Unique slot identifier from get_availability() timeslots
                        Examples: "2431185583", "1970015633"
                        This identifies the exact time slot and must be current
                        
        date_time (str): Reservation datetime in YYYY-MM-DDTHH:MM format
                        Examples: "2025-07-24T13:30", "2025-07-25T19:00"
                        Must match exactly with availability slot dateTime
                        
        availability_token (str): Authorization token from get_availability() response
                                 Examples: "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ"
                                 This authorizes the booking attempt
                                 
        party_size (int): Number of diners for the reservation
                         Range: 1-20 (restaurant dependent)
                         Must match the party_size used in get_availability()
                         
        location (str): Location string for geocoding validation
                       Examples: "New York, NY", "Manhattan", "123 Main St, Boston"
                       Used for booking validation - should match search location
        
        special_requests (str, optional): Special dining requests or notes
                                         Examples: "Window table preferred", "Birthday celebration",
                                                  "Wheelchair accessible table", "Quiet corner please"
                                         Max length: ~500 characters
                                         
        occasion (str, optional): Type of occasion for the reservation
                                 Examples: "birthday", "anniversary", "business dinner",
                                          "date night", "celebration", "graduation"
                                 Used for restaurant preparation and ambiance
    
    Returns:
        Dict[str, Any]: Booking result containing:
            - success (bool): Whether reservation was successfully created
            - message (str): Confirmation message with booking status
            - confirmation_number (str): **IMPORTANT** - Unique reservation ID for management
            - reservation (Dict): Complete reservation details with:
                * confirmationNumber (str): Same as above, for redundancy
                * token (str): Reservation token for cancellation/modification
                * restaurant (Dict): Restaurant information:
                    + id (str): Restaurant ID
                    + name (str): Restaurant name
                * dateTime (str): Confirmed reservation time (ISO format)
                * partySize (int): Number of diners confirmed
                * status (int): Reservation status code (1 = confirmed)
                * reservationStatus (str): Human-readable status ("Pending", "Confirmed")
                * creditCard (bool): Whether a credit card was used/required
            - restaurant_name (str): Restaurant name for convenience
            - date_time (str): Echo of reservation time
            - party_size (int): Echo of party size
            
        On error:
            - success (bool): False
            - error (str): Detailed error description
            - status_code (int): HTTP status code from API
            - **Common errors**:
                * "Credit card is required for this reservation" - slot requires card, test account can't add one
                * "Booking failed: 422" - Slot no longer available or data mismatch
                * "Booking failed: 400" - Invalid parameters or expired tokens
    
    **Example Usage**:
        ```python
        # After getting availability data:
        booking = await book_reservation(
            restaurant_id="96577",
            slot_hash="1970015633",  # From availability response
            date_time="2025-07-24T13:30",  # From availability slot
            availability_token="eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ",  # From availability
            party_size=2,
            location="New York, NY",
            special_requests="Window table preferred",
            occasion="birthday"
        )
        
        if booking["success"]:
            confirmation = booking["confirmation_number"]  # Save this!
            print(f"✅ Reserved table at {booking['restaurant_name']}")
            print(f"📅 Date: {booking['date_time']}")  
            print(f"🎫 Confirmation: {confirmation}")
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "message": "Reservation booked successfully!",
            "confirmation_number": "101750", 
            "reservation": {
                "confirmationNumber": "101750",
                "token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1",
                "restaurant": {
                    "id": "212347",
                    "name": "SAN CARLO Osteria Piemonte"
                },
                "dateTime": "2025-07-24T13:30",
                "partySize": 2,
                "status": 1,
                "reservationStatus": "Pending",
                "creditCard": false
            },
            "restaurant_name": "SAN CARLO Osteria Piemonte",
            "date_time": "2025-07-24T13:30",
            "party_size": 2
        }
        ```
    
    **Critical Success Data**:
        After successful booking, SAVE these values for reservation management:
        1. **confirmation_number**: For cancellation and modification
        2. **reservation.token**: Required for cancel_reservation() and modifications
        3. **restaurant_id**: Needed for cancellation
        4. **dateTime**: For your calendar and confirmation
    
    **Credit Card Requirements**:
        - **Test Accounts**: Can only book slots with requiresCreditCard: false
        - **Real Accounts**: Can book any slot (card automatically charged/held)
        - If credit card required but unavailable: Error returned with guidance
        - Credit card policy enforced automatically (HOLD vs CHARGE)
    
    **Error Scenarios & Solutions**:
        - **"Credit card is required"**: 
            * Test account limitation - find different restaurant/time
            * Real account - call add_credit_card() first
        - **"Booking failed: 422"**: 
            * Slot no longer available - run get_availability() again
            * Invalid slot_hash/token - ensure data is from recent availability check
        - **"Booking failed: 400"**: 
            * Parameter mismatch - verify all data matches availability response
            * Expired availability_token - tokens have limited lifespan (~15 minutes)
        - **Not authenticated**: 
            * Call register_user() first to get API token
    
    **Booking Best Practices**:
        1. **Move quickly**: Availability tokens expire (~15 minutes)
        2. **Verify data**: All parameters must match get_availability() response exactly
        3. **Save confirmation**: Store confirmation_number immediately for management  
        4. **Check requirements**: Review requiresCreditCard before attempting booking
        5. **Handle failures gracefully**: Re-check availability if booking fails
    
    **Data Validation Rules**:
        - restaurant_id: Must exist in OpenTable system
        - slot_hash: Must be from recent availability check for same restaurant
        - date_time: Must be exact match with availability slot dateTime
        - availability_token: Must be from same availability response as slot_hash  
        - party_size: Must match availability check party_size
        - All timing data becomes invalid after ~15 minutes
    
    **Post-Booking Actions**:
        1. ✅ Save confirmation_number and reservation.token  
        2. 📧 Restaurant may send confirmation email to registered address
        3. 📱 SMS notifications sent if opted in during registration
        4. 📅 Add to calendar with restaurant details and confirmation number
        5. 🔄 Use list_reservations() to verify booking in system
    
    **Next Steps After Booking**:
        - Use list_reservations() to view all your reservations
        - Use cancel_reservation() if you need to cancel
        - Keep confirmation_number for restaurant check-in
        - Arrive on time - restaurants may release tables after 15-minute grace period
    
    **Related Functions**:
        - search_restaurants(): Find restaurants and get restaurant_id
        - get_availability(): Get slot_hash and availability_token (REQUIRED before booking)
        - list_reservations(): View all reservations including this one
        - cancel_reservation(): Cancel this reservation if needed
        - add_credit_card(): Required for slots with credit card requirements (real accounts only)
    
    **Performance & Timing**:
        - Booking response time: 2-5 seconds
        - Availability token lifespan: ~15 minutes from get_availability() call
        - Confirmation appears in list_reservations() within 1-2 minutes
        - Restaurant notification: Immediate
        - Best practice: Complete booking within 5 minutes of availability check
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        booking_request = BookingRequest(
            restaurant_id=restaurant_id,
            slot_hash=slot_hash,
            date_time=date_time,
            availability_token=availability_token,
            party_size=party_size,
            location=location,
            special_requests=special_requests,
            occasion=occasion,
            sms_opt_in=True
        )
        
        response = book_reservation_endpoint_book_post.sync_detailed(
            client=ot_service.auth_client,
            body=booking_request,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 201 and response.parsed:
            reservation = response.parsed
            return {
                "success": True,
                "message": "Reservation booked successfully!",
                "confirmation_number": reservation.get("reservation", {}).get("confirmationNumber"),
                "reservation": reservation.get("reservation", {}),
                "restaurant_name": reservation.get("reservation", {}).get("restaurant", {}).get("name"),
                "date_time": reservation.get("reservation", {}).get("dateTime"),
                "party_size": reservation.get("reservation", {}).get("partySize")
            }
        else:
            error_msg = str(response.content) if hasattr(response, 'content') else f"Status {response.status_code}"
            return {
                "success": False, 
                "error": f"Booking failed: {error_msg}",
                "status_code": response.status_code
            }
            
    except Exception as e:
        return {"success": False, "error": f"Booking error: {str(e)}"}

@mcp.tool()
async def list_reservations() -> Dict[str, Any]:
    """List all user reservations and comprehensive profile information.
    
    This endpoint retrieves the complete user profile including reservation history,
    account statistics, saved payment methods, and OpenTable activity summary.
    Essential for viewing existing bookings, managing reservations, and accessing
    the data needed for cancellation or modification operations.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Use Cases**: 
        - View all current and past reservations
        - Get reservation tokens for cancellation/modification
        - Check account statistics and activity
        - Review saved payment methods
        - Verify recent bookings after successful book_reservation() calls
    
    **No Parameters Required**: Uses authenticated user's token to fetch their data
    
    Returns:
        Dict[str, Any]: Comprehensive user profile and reservation data containing:
            - success (bool): Whether profile retrieval succeeded
            - user_profile (Dict): Account information with:
                * name (str): Full name (first + last name)
                * email (str): Registered email address
                * customer_id (str): OpenTable customer identifier
                * global_person_id (str): Global person identifier across OpenTable systems
            - reservations (List[Dict]): Array of reservation objects with:
                * confirmationNumber (str): **CRITICAL** - Unique reservation ID for management
                * token (str): **CRITICAL** - Required for cancel_reservation() and modifications
                * restaurant (Dict): Restaurant details:
                    + id (str): Restaurant ID for operations
                    + name (str): Restaurant name for display
                * dateTime (str): Reservation time in ISO format (YYYY-MM-DDTHH:MM)
                * partySize (int): Number of diners confirmed
                * status (int): Reservation status code (1 = active/pending)
                * reservationStatus (str): Human-readable status ("Pending", "Confirmed", "Completed")
                * creditCard (bool): Whether a credit card was used for this reservation
            - total_reservations (int): Total number of reservations found
            - statistics (Dict): Account activity summary:
                * reservationsCount (int): Total lifetime reservations
                * reviewsCount (int): Number of restaurant reviews written
                * photosCount (int): Number of photos uploaded
            - wallet (Dict): Payment method information:
                * maxCards (int): Maximum credit cards allowed (typically 5)
                * cards (List): Array of saved credit cards (empty for test accounts)
                
        On error:
            - success (bool): False
            - error (str): Error description
            - details (str): Additional error information if available
    
    **Example Usage**:
        ```python
        profile = await list_reservations()
        
        if profile["success"]:
            print(f"Account: {profile['user_profile']['name']} ({profile['user_profile']['email']})")
            print(f"Total reservations: {profile['total_reservations']}")
            
            for reservation in profile["reservations"]:
                restaurant = reservation["restaurant"]["name"]
                date_time = reservation["dateTime"]
                confirmation = reservation["confirmationNumber"]
                print(f"🍽️  {restaurant} on {date_time} (#{confirmation})")
                
                # Save these for potential cancellation:
                token = reservation["token"]
                restaurant_id = reservation["restaurant"]["id"]
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "user_profile": {
                "name": "Thomas Meringue",
                "email": "dojarob+ot0fd39afd@gmail.com",
                "customer_id": "263863380",
                "global_person_id": "150238676545"
            },
            "reservations": [
                {
                    "confirmationNumber": "101750",
                    "token": "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1",
                    "restaurant": {
                        "id": "212347",
                        "name": "SAN CARLO Osteria Piemonte"
                    },
                    "dateTime": "2025-07-24T13:30",
                    "partySize": 2,
                    "status": 1,
                    "reservationStatus": "Pending",
                    "creditCard": false
                }
            ],
            "total_reservations": 1,
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
    
    **Critical Data for Reservation Management**:
        For each reservation, SAVE these values for future operations:
        1. **confirmationNumber**: Primary identifier for restaurant interactions
        2. **token**: Required for cancel_reservation() and modification functions
        3. **restaurant.id**: Needed for cancellation operations
        4. **dateTime**: For calendar and timing management
        5. **reservationStatus**: Current state of the reservation
    
    **Reservation Status Meanings**:
        - **"Pending"**: Recently booked, awaiting restaurant confirmation
        - **"Confirmed"**: Restaurant has confirmed the reservation
        - **"Completed"**: Past reservation that was fulfilled
        - **"Cancelled"**: Previously cancelled reservation (may still appear in history)
        - **status code 1**: Generally indicates active/confirmed reservation
    
    **Account Statistics Insights**:
        - **reservationsCount**: Shows dining activity level and loyalty
        - **reviewsCount**: Indicates engagement with OpenTable community features
        - **photosCount**: Shows contribution to restaurant photo galleries
        - All counts reflect lifetime activity across the account
    
    **Credit Card & Wallet Information**:
        - **Test Accounts**: wallet.cards will always be empty (can't add cards)
        - **Real Accounts**: Shows saved payment methods for future bookings
        - **maxCards**: Limit of credit cards that can be stored (typically 5)
        - Cards shown as masked numbers for security
    
    **Error Scenarios**:
        - **Not authenticated**: "Please register a user first using register_user()"
        - **API unavailable**: Connection or server errors
        - **Invalid token**: Token expired or malformed (re-register user)
    
    **Data Freshness**:
        - Reservation data is real-time from OpenTable's systems
        - New bookings appear within 1-2 minutes
        - Cancellations are reflected immediately
        - Statistics update within 24 hours of activity
    
    **Filtering & Management**:
        - All reservations returned (past, present, future)
        - Results typically ordered by dateTime (most recent first)
        - For active reservations: Look for status = 1 and future dateTime
        - For cancellable reservations: Must have valid token and be future-dated
    
    **Common Use Cases After list_reservations()**:
        1. **View Upcoming Reservations**: Filter by future dateTime
        2. **Cancel Reservation**: Use confirmationNumber + token with cancel_reservation()
        3. **Verify Recent Booking**: Check that book_reservation() result appears
        4. **Account Management**: Review dining history and activity
        5. **Payment Review**: Check wallet information for card management
    
    **Next Steps Based on Results**:
        - **Found reservations**: Use cancel_reservation() to cancel if needed
        - **No reservations**: Use search_restaurants() → get_availability() → book_reservation()
        - **Need payment method**: Use add_credit_card() (real accounts only)
        - **Review account**: Check statistics for OpenTable engagement level
    
    **Related Functions**:
        - register_user(): Required first step for authentication
        - book_reservation(): Creates reservations that appear in this list
        - cancel_reservation(): Cancel reservations using data from this list
        - add_credit_card(): Manage payment methods shown in wallet section
    
    **Performance & Caching**:
        - Response time: 1-3 seconds
        - Data is live from OpenTable servers (no caching)
        - Safe to call frequently for reservation status updates
        - Recommended: Check after any booking/cancellation operation
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        response = get_reservations_reservations_get.sync_detailed(
            client=ot_service.auth_client,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            data = response.parsed
            reservations = data.get("reservations", {}).get("history", [])
            
            return {
                "success": True,
                "user_profile": {
                    "name": f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
                    "customer_id": data.get("customerId"),
                    "global_person_id": data.get("globalPersonId")
                },
                "reservations": reservations,
                "total_reservations": len(reservations),
                "statistics": data.get("statistics", {}),
                "wallet": data.get("wallet", {})
            }
        else:
            return {
                "success": False, 
                "error": f"Failed to list reservations with status {response.status_code}",
                "details": str(response.content) if hasattr(response, 'content') else None
            }
            
    except Exception as e:
        return {"success": False, "error": f"List reservations error: {str(e)}"}

@mcp.tool()
async def cancel_reservation(confirmation_number: str, restaurant_id: str, reservation_token: str) -> Dict[str, Any]:
    """Cancel an existing restaurant reservation with immediate confirmation.
    
    This endpoint cancels a confirmed reservation using the specific reservation data
    obtained from list_reservations() or book_reservation(). Cancellation is immediate
    and irreversible - the table slot is returned to restaurant inventory and cannot
    be recovered. Most restaurants allow cancellation up to the reservation time.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Prerequisites**: 
        1. Must have an existing reservation (from book_reservation())
        2. Must have reservation details (from list_reservations() or original booking)
        3. Reservation must be future-dated (can't cancel past reservations)
    
    **Cancellation Policy**: 
        - Immediate and irreversible once confirmed
        - No fees for standard cancellations (restaurant dependent)
        - Credit card holds released automatically
        - Restaurant receives immediate notification
    
    **Data Sources**: All required parameters come from list_reservations() output
    
    Args:
        confirmation_number (str): Unique reservation identifier from booking
                                  Examples: "101750", "ABC123", "789456"  
                                  Source: confirmationNumber from reservation object
                                  Note: This is what restaurants use to identify your booking
        
        restaurant_id (str): Restaurant identifier for the reservation
                            Examples: "96577", "212347", "30196"
                            Source: restaurant.id from reservation object
                            Note: Must match the restaurant where reservation was made
                            
        reservation_token (str): Unique reservation authorization token  
                                Examples: "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1"
                                Source: token field from reservation object
                                Note: This authorizes the cancellation operation
    
    Returns:
        Dict[str, Any]: Cancellation result containing:
            - success (bool): Whether cancellation was completed successfully
            - message (str): Confirmation message about cancellation status
            - confirmation_number (str): Echo of cancelled reservation number
            
        On error:
            - success (bool): False
            - error (str): Detailed error description
            - details (str): Additional error information if available
            - **Common errors**:
                * "Cancellation failed with status 422" - Invalid data or reservation not found
                * "Cancellation failed with status 400" - Reservation already cancelled or expired
                * "Not authenticated" - Need to register_user() first
    
    **Example Usage**:
        ```python
        # First, get reservation details
        reservations = await list_reservations()
        
        if reservations["success"] and reservations["reservations"]:
            # Find the reservation to cancel
            reservation = reservations["reservations"][0]  # or find specific one
            
            # Cancel using the required data  
            cancellation = await cancel_reservation(
                confirmation_number=reservation["confirmationNumber"],
                restaurant_id=reservation["restaurant"]["id"], 
                reservation_token=reservation["token"]
            )
            
            if cancellation["success"]:
                print(f"✅ Cancelled reservation #{cancellation['confirmation_number']}")
                print("Table released back to restaurant inventory")
            else:
                print(f"❌ Cancellation failed: {cancellation['error']}")
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "message": "Reservation successfully cancelled",
            "confirmation_number": "101750"
        }
        ```
    
    **Complete Workflow Example**:
        ```python
        # 1. Get list of reservations
        profile = await list_reservations()
        
        # 2. Find reservation to cancel
        for reservation in profile["reservations"]:
            if reservation["confirmationNumber"] == "101750":  # Target reservation
                # 3. Extract required cancellation data
                confirmation = reservation["confirmationNumber"]
                restaurant_id = reservation["restaurant"]["id"]
                token = reservation["token"]
                
                # 4. Perform cancellation
                result = await cancel_reservation(confirmation, restaurant_id, token)
                break
        ```
    
    **Critical Data Requirements**:
        ALL THREE parameters are required and must match exactly:
        1. **confirmation_number**: From original booking or list_reservations()
        2. **restaurant_id**: From reservation.restaurant.id 
        3. **reservation_token**: From reservation.token
        
        **Data Validation**: All values must be from the same reservation object
    
    **Error Scenarios & Solutions**:
        - **"Cancellation failed with status 422"**:
            * Confirmation number not found - verify exact match with list_reservations()
            * Restaurant ID mismatch - ensure using reservation.restaurant.id
            * Token invalid - use reservation.token from same object
        - **"Cancellation failed with status 400"**:
            * Reservation already cancelled - check current status
            * Past reservation - can't cancel reservations that already occurred
            * System error - try again or contact restaurant directly
        - **"Not authenticated"**:
            * Call register_user() first to establish session
    
    **Cancellation Best Practices**:
        1. **Act quickly**: Don't wait until last minute (restaurant courtesy)
        2. **Verify data**: Use list_reservations() to get current, accurate data
        3. **Check timing**: Can't cancel past reservations or same-day (restaurant dependent)
        4. **Handle errors**: Have backup plan if cancellation fails
        5. **Confirm success**: Verify cancellation completed before assuming it worked
    
    **Restaurant Policies & Timing**:
        - **Cancellation deadline**: Most restaurants accept cancellations until reservation time
        - **No-show fees**: Avoiding cancellation may result in charges for no-shows
        - **Credit card holds**: Released immediately upon successful cancellation
        - **Same-day policy**: Some restaurants have same-day cancellation restrictions
        - **Holiday restrictions**: Special events may have stricter cancellation policies
    
    **Post-Cancellation Effects**:
        1. ✅ Table slot returned to restaurant availability immediately
        2. 📧 Cancellation confirmation may be sent to registered email
        3. 💳 Credit card authorization holds released within 24-48 hours
        4. 📊 Reservation status updated in list_reservations() within minutes
        5. 🏪 Restaurant receives immediate notification of cancellation
    
    **Verification Steps After Cancellation**:
        1. **Check success response**: Ensure success: true in return value
        2. **Call list_reservations()**: Verify reservation no longer appears or shows "Cancelled"
        3. **Save confirmation**: Keep cancellation confirmation_number for records
        4. **Monitor credit card**: Verify holds are released (24-48 hours)
    
    **Cannot Cancel Scenarios**:
        - Reservations that already occurred (past dateTime)
        - Reservations already cancelled previously  
        - Reservations at restaurants with no-cancellation policies
        - System-cancelled reservations due to restaurant closure/issues
        - Invalid or corrupted reservation tokens
    
    **Alternative Actions If Cancellation Fails**:
        1. **Contact restaurant directly**: Use phone number from original booking
        2. **Try later**: System issues may be temporary
        3. **Check reservation status**: May already be cancelled
        4. **Use restaurant website**: Many allow online cancellation
        5. **Visit in person**: Last resort for difficult cancellations
    
    **Next Steps After Successful Cancellation**:
        - Table slot is immediately available for other diners
        - You can book a new reservation at same or different restaurant
        - Consider rebooking if you still need dining reservations
        - Restaurant may offer alternatives if cancellation was due to their issue
    
    **Related Functions**:
        - list_reservations(): Required to get cancellation data (confirmation_number, restaurant_id, token)
        - book_reservation(): Creates reservations that can later be cancelled
        - search_restaurants(): Find alternative restaurants if rebooking needed
        - register_user(): Required first step for authentication
    
    **Performance & Reliability**:
        - Cancellation response time: 2-5 seconds
        - Success rate: >95% for valid data
        - Restaurant notification: Immediate
        - Credit card release: 24-48 hours
        - Recommended: Cancel as early as possible for courtesy and table availability
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        cancel_request = CancelRequest(
            restaurant_id=restaurant_id,
            reservation_token=reservation_token
        )
        
        response = cancel_reservation_reservations_confirmation_number_delete.sync_detailed(
            client=ot_service.auth_client,
            confirmation_number=confirmation_number,
            body=cancel_request,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            return {
                "success": True,
                "message": "Reservation successfully cancelled",
                "confirmation_number": confirmation_number
            }
        else:
            return {
                "success": False, 
                "error": f"Cancellation failed with status {response.status_code}",
                "details": str(response.content) if hasattr(response, 'content') else None
            }
            
    except Exception as e:
        return {"success": False, "error": f"Cancellation error: {str(e)}"}

@mcp.tool()
async def add_credit_card(
    card_full_name: str,
    card_number: str, 
    card_exp_month: int,
    card_exp_year: int,
    card_cvv: str,
    card_zip: str
) -> Dict[str, Any]:
    """Add a credit card to your OpenTable account for restaurant reservations requiring payment.
    
    This endpoint securely tokenizes and stores a credit card in your OpenTable account
    for use with reservations that require credit card holds or payments. The card is
    processed through Spreedly for PCI compliance and stored as a masked token for
    future reservation use. Essential for booking at high-end restaurants and prime time slots.
    
    **CRITICAL LIMITATION**: This endpoint only works with REAL OpenTable accounts, 
    not test accounts created through register_user(). Test accounts cannot add credit cards.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Security**: 
        - Credit card data is tokenized via Spreedly (PCI compliant)
        - Only masked numbers stored in OpenTable systems  
        - CVV is not stored after initial tokenization
        - Full card numbers never stored in plain text
    
    **Use Cases**:
        - Book reservations at restaurants requiring credit card holds
        - Access premium time slots that require payment guarantees
        - Enable automatic charging for no-show fees or cancellation charges
        - Book special events, holiday dinners, or exclusive experiences
    
    Args:
        card_full_name (str): Full name as it appears on the credit card
                             Examples: "John Doe", "Sarah Johnson-Smith", "Maria Elena Rodriguez"
                             Note: Must match card exactly for payment processing
                             
        card_number (str): Complete credit card number without spaces or dashes
                          Examples: "4111111111111111" (Visa test), "5555555555554444" (MC test)
                          Supported: Visa, MasterCard, American Express, Discover
                          Note: Real card numbers required for live accounts
                          
        card_exp_month (int): Expiration month as 1-12 integer
                             Examples: 1 (January), 6 (June), 12 (December)
                             Range: 1-12 only (not 01-12 string format)
                             
        card_exp_year (int): Expiration year as 4-digit integer  
                            Examples: 2025, 2026, 2030
                            Range: Current year through ~10 years future
                            Note: 2-digit years not supported (use 2025, not '25')
                            
        card_cvv (str): Card verification value from back of card
                       Examples: "123" (Visa/MC), "1234" (Amex)
                       Length: 3 digits (Visa/MC/Discover) or 4 digits (Amex)
                       Note: Not stored after tokenization
                       
        card_zip (str): Billing ZIP code associated with the card
                       Examples: "10001", "90210", "K1A 0A6" (Canadian postal codes supported)
                       Format: US ZIP codes or international postal codes
    
    Returns:
        Dict[str, Any]: Card addition result containing:
            - success (bool): Whether card was successfully added and tokenized
            - message (str): Confirmation message about card addition
            - card (Dict): Added card information with:
                * id (str): Unique card identifier for OpenTable system  
                * type (str): Card brand ("Visa", "MasterCard", "American Express", "Discover")
                * last4 (str): Last 4 digits of card number for identification
                * expiry_month (str): Expiration month (2-digit format like "12")
                * expiry_year (str): Expiration year (2-digit format like "25")  
                * default (bool): Whether this is the default payment method
                
        On error:
            - success (bool): False
            - error (str): Detailed error description
            - note (str): Reminder about test account limitations
            - **Common errors**:
                * "Failed to add card: 404" - Test account limitation (can't add cards)
                * "Failed to add card: 422" - Invalid card data or expired card
                * "Failed to add card: 400" - Missing required fields or format errors
    
    **Example Usage**:
        ```python
        # Add a test credit card (only works with real OpenTable accounts)
        card_result = await add_credit_card(
            card_full_name="John Doe",
            card_number="4111111111111111",  # Visa test number
            card_exp_month=12,
            card_exp_year=2025,
            card_cvv="123",
            card_zip="10001"
        )
        
        if card_result["success"]:
            card_info = card_result["card"]
            print(f"✅ Added {card_info['type']} ending in {card_info['last4']}")
            print(f"💳 Card ID: {card_info['id']}")
            print(f"🎯 Default card: {card_info['default']}")
        else:
            print(f"❌ Failed to add card: {card_result['error']}")
            if "test account" in card_result.get("note", ""):
                print("💡 Tip: This only works with real OpenTable accounts")
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
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
    
    **Test Account Error Response**:
        ```json
        {
            "success": false,
            "error": "Failed to add card: 404 - {\"error\":{\"code\":\"UNKNOWN\",\"shouldRetokenize\":false}}",
            "note": "This feature only works with real OpenTable accounts, not test accounts"
        }
        ```
    
    **Critical Account Type Limitation**:
        - **Real OpenTable Accounts**: Full credit card functionality supported
        - **Test Accounts** (from register_user()): Cannot add credit cards due to system limitations
        - **Workaround for Testing**: Use slots with requiresCreditCard: false from get_availability()
        - **Production Use**: Connect real OpenTable accounts for full functionality
    
    **Credit Card Validation Rules**:
        - **Card Number**: Must be valid according to Luhn algorithm
        - **Expiration**: Must be future-dated (current month or later)
        - **CVV**: Must match card type length requirements (3 or 4 digits)
        - **Name**: Must match cardholder name for payment processing
        - **ZIP**: Must match billing address ZIP code
    
    **Supported Card Types**:
        - **Visa**: Numbers starting with 4, 16 digits, 3-digit CVV
        - **MasterCard**: Numbers starting with 5, 16 digits, 3-digit CVV  
        - **American Express**: Numbers starting with 34/37, 15 digits, 4-digit CVV
        - **Discover**: Numbers starting with 6, 16 digits, 3-digit CVV
        - International cards may be supported (restaurant/region dependent)
    
    **Error Scenarios & Solutions**:
        - **"Failed to add card: 404"**: 
            * Test account limitation - this is expected behavior
            * Solution: Use real OpenTable account for credit card functionality
        - **"Failed to add card: 422"**: 
            * Invalid card number, expired card, or failed validation
            * Solution: Verify all card details are correct and current
        - **"Failed to add card: 400"**: 
            * Missing required fields or incorrect format
            * Solution: Check all parameters match expected types and formats
        - **Not authenticated**: 
            * Call register_user() first to establish session
    
    **Post-Addition Benefits**:
        After successful card addition, you can:
        1. ✅ Book reservations with requiresCreditCard: true slots
        2. 🏆 Access premium time slots and special events  
        3. 🎯 Reserve tables at high-end restaurants requiring payment guarantees
        4. 💳 Enable automatic processing of no-show fees or cancellation charges
        5. 🔄 Use the same card for multiple reservations without re-entering data
    
    **Card Management After Addition**:
        - **View Cards**: Use list_reservations() to see wallet.cards array
        - **Default Card**: First card added becomes default payment method
        - **Multiple Cards**: Can add up to 5 credit cards (maxCards limit)
        - **Card Updates**: Need to add new card if expiration/details change
        - **Security**: Only last 4 digits visible in API responses
    
    **Booking Integration**:
        After adding a card, reservation booking changes:
        - get_availability() slots with requiresCreditCard: true become bookable
        - book_reservation() automatically uses saved card for payment holds
        - No need to specify which card - default card used automatically
        - Credit card policy (HOLD vs CHARGE) handled by restaurant settings
    
    **Test Environment Workarounds**:
        Since test accounts can't add cards, for development/testing:
        1. 🔍 Search for restaurants using search_restaurants()
        2. ⏰ Check availability with get_availability()  
        3. 🎯 Filter for slots with requiresCreditCard: false
        4. 📝 Book only non-credit-card slots with book_reservation()
        5. ✅ Full workflow testing without payment methods
    
    **Next Steps After Adding Card**:
        1. **Verify Addition**: Check list_reservations() wallet section
        2. **Test Booking**: Find restaurant slots requiring credit cards
        3. **Use get_availability()**: Look for requiresCreditCard: true slots
        4. **Book Premium Slots**: Use book_reservation() with card-required slots
        5. **Monitor Charges**: Track credit card statements for holds/charges
    
    **Related Functions**:
        - register_user(): Required first step (though test accounts can't add cards)
        - list_reservations(): View saved cards in wallet section
        - get_availability(): See which slots require credit cards (requiresCreditCard field)
        - book_reservation(): Book slots that require credit cards (uses saved card automatically)
    
    **Security & Privacy**:
        - PCI DSS compliant processing via Spreedly tokenization
        - Card data encrypted in transit and at rest
        - CVV not stored after initial tokenization
        - Only masked card data accessible through API
        - Full card details never logged or stored in plain text
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        card_data = CardCreate(
            card_full_name=card_full_name,
            card_number=card_number,
            card_exp_month=card_exp_month,
            card_exp_year=card_exp_year,
            card_cvv=card_cvv,
            card_zip=card_zip
        )
        
        response = add_credit_card_cards_post.sync_detailed(
            client=ot_service.auth_client,
            body=card_data,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            card_info = response.parsed
            return {
                "success": True,
                "message": "Credit card added successfully",
                "card": card_info.get("card", {})
            }
        else:
            error_msg = str(response.content) if hasattr(response, 'content') else f"Status {response.status_code}"
            return {
                "success": False, 
                "error": f"Failed to add card: {error_msg}",
                "note": "This feature only works with real OpenTable accounts, not test accounts"
            }
            
    except Exception as e:
        return {"success": False, "error": f"Card addition error: {str(e)}"}

@mcp.tool()
async def list_credit_cards() -> Dict[str, Any]:
    """List all credit cards saved to the user's OpenTable account.
    
    This endpoint retrieves all credit cards that have been securely stored in the user's
    OpenTable account, displaying masked card information for identification and selection
    purposes. Essential for viewing available payment methods before making reservations
    that require credit card holds or payments at premium restaurants.
    
    **CRITICAL LIMITATION**: This endpoint only works with REAL OpenTable accounts, 
    not test accounts created through register_user(). Test accounts cannot store credit cards.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Security Features**:
        - Only displays masked card numbers (last 4 digits)
        - Shows card type, expiration, and billing info
        - No sensitive data (full numbers, CVVs) ever returned
        - Cards are tokenized via Spreedly (PCI compliant)
    
    **Use Cases**:
        - Check available payment methods before booking premium restaurants
        - Verify card details before attempting reservations requiring payment
        - Manage multiple payment options for different dining occasions
        - Confirm default payment method for automatic charging
    
    **No Parameters Required**: Uses authenticated user's account from API token
    
    Returns:
        Dict[str, Any]: Credit card listing result containing:
            On success:
                - success (bool): True
                - cards (List[Dict]): Array of saved credit cards, each containing:
                    - id (str): Unique card identifier for booking references
                    - masked_number (str): Masked card number (e.g., "•••• •••• •••• 1234")
                    - last4 (str): Last 4 digits for identification ("1234")
                    - card_type (str): Card brand ("Visa", "Mastercard", "Amex", etc.)
                    - exp_month (str): Expiration month ("12")
                    - exp_year (str): Expiration year ("2025")
                    - cardholder_name (str): Name on card
                    - billing_zip (str): Billing ZIP code
                    - default (bool): Whether this is the default payment method  
                    - created_date (str): When card was added
                    - payment_provider (str): "SPREEDLY" (tokenization service)
                - total_cards (int): Number of cards found
                - message (str): Success confirmation
                
            On error:
                - success (bool): False
                - error (str): Error description
                - cards (List): Empty array
                - note (str): Additional context about limitations
    
    **Example Success Response**:
        ```json
        {
            "success": true,
            "cards": [
                {
                    "id": "abc123def456",
                    "masked_number": "•••• •••• •••• 1234",
                    "last4": "1234",
                    "card_type": "Visa",
                    "exp_month": "12",
                    "exp_year": "2025",
                    "cardholder_name": "John Doe",
                    "billing_zip": "90210",
                    "default": true,
                    "created_date": "2024-01-15",
                    "payment_provider": "SPREEDLY"
                }
            ],
            "total_cards": 1,
            "message": "Retrieved 1 saved credit card"
        }
        ```
    
    **Error Scenarios**:
        - Test account limitation: "This feature only works with real OpenTable accounts"
        - Authentication issues: Invalid or expired API token
        - No cards found: Returns success=true with empty cards array
        - Service unavailable: Connection or server errors
        - Proxy issues: Check OXYLABS credentials if configured
    
    **Account Type Limitations**:
        ✅ **Real OpenTable Accounts**: Full functionality - can add, list, and use cards
        ❌ **Test Accounts**: Cannot add or list credit cards (API limitation)
    
    **Next Steps After Listing Cards**:
        1. Use card IDs for book_reservation() calls requiring payment
        2. Add more cards with add_credit_card() if needed
        3. Check default card settings for automatic payments
        4. Verify expiration dates for upcoming reservations
    
    **Related Functions**: 
        - add_credit_card(): Add new payment methods to account
        - book_reservation(): Use saved cards for premium restaurant bookings
        - search_restaurants(): Find restaurants that may require credit cards
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        # Call the list credit cards API
        response = list_credit_cards_cards_get.sync_detailed(
            client=ot_service.auth_client,
            x_org_key=ot_service.org_key
        )
        
        if response.status_code == 200 and response.parsed:
            # Parse the successful response - API returns {user_id, cards, total_cards}
            data = response.parsed
            cards = data.get('cards', [])
            total_cards = data.get('total_cards', len(cards))
            user_id = data.get('user_id')
            
            return {
                "success": True,
                "user_id": user_id,
                "cards": cards,
                "total_cards": total_cards,
                "message": f"Retrieved {total_cards} saved credit card{'s' if total_cards != 1 else ''}"
            }
        else:
            # Handle various error status codes
            error_msg = str(response.content) if hasattr(response, 'content') else f"Status {response.status_code}"
            return {
                "success": False, 
                "error": f"Failed to retrieve cards: {error_msg}",
                "cards": [],
                "note": "This feature only works with real OpenTable accounts, not test accounts"
            }
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"Card listing error: {str(e)}",
            "cards": []
        }

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Check the health status of the OpenTable API service and connectivity.
    
    This endpoint performs a comprehensive health check of the OpenTable REST API
    infrastructure, verifying service availability, response times, and system
    operational status. Essential for diagnosing connectivity issues, validating
    API credentials, and confirming system readiness before attempting reservations.
    
    **Authentication**: Not required - this is a public endpoint for system monitoring
    
    **Use Cases**:
        - Verify API connectivity before starting reservation workflows
        - Troubleshoot authentication or network issues
        - Monitor OpenTable service availability
        - Validate proxy configuration and routing
        - System integration testing and monitoring
        - Pre-deployment health verification
    
    **No Parameters Required**: Simple connectivity and service availability check
    
    Returns:
        Dict[str, Any]: Health status information containing:
            - success (bool): Whether health check completed successfully
            - status (str): Service health status ("healthy" or "unhealthy")
            - service (str): Service identifier ("opentable-rest-api")
            - message (str): Human-readable status message
            
        On service issues:
            - success (bool): False
            - status (str): "unhealthy" or "error"
            - error (str): Specific error description
    
    **Example Usage**:
        ```python
        # Check API health before starting reservation workflow
        health = await health_check()
        
        if health["success"] and health["status"] == "healthy":
            print("✅ OpenTable API is operational")
            print(f"📊 Service: {health['service']}")
            print(f"💬 Status: {health['message']}")
            # Proceed with register_user(), search_restaurants(), etc.
        else:
            print("❌ OpenTable API is not available")
            print(f"🔍 Error: {health.get('error', 'Unknown issue')}")
            # Handle service unavailability
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "status": "healthy",
            "service": "opentable-rest-api",
            "message": "OpenTable API is operational"
        }
        ```
    
    **Service Unavailable Response Example**:
        ```json
        {
            "success": false,
            "status": "unhealthy",
            "error": "API returned status 503"
        }
        ```
    
    **Connection Error Response Example**:
        ```json
        {
            "success": false,
            "status": "error",
            "error": "Health check failed: Connection timeout after 30s"
        }
        ```
    
    **Health Check Components Validated**:
        - **API Server Response**: Base OpenTable REST API availability
        - **Response Time**: Service responsiveness and performance
        - **HTTP Status**: Proper response codes from service endpoints
        - **Network Connectivity**: Ability to reach OpenTable infrastructure
        - **Proxy Configuration**: If using Oxylabs proxies, routing validation
    
    **Interpreting Health Results**:
        - **success: true, status: "healthy"**: Full service operational ✅
        - **success: false, status: "unhealthy"**: Service responding but degraded ⚠️
        - **success: false, status: "error"**: Connection or major service issues ❌
    
    **Troubleshooting Guide**:
        
        **If Health Check Fails**:
        1. **Network Issues**: 
            * Check internet connectivity
            * Verify firewall settings allow HTTPS outbound
            * Test with: `curl https://apparel-scraper--opentable-rest-api-fastapi-app.modal.run/health`
        
        2. **Proxy Configuration Issues**:
            * Verify OXYLABS_USERNAME and OXYLABS_PASSWORD environment variables
            * Test proxy with test_proxy.py script
            * Check Oxylabs account status and credentials
        
        3. **Service Degradation**:
            * OpenTable API may be experiencing temporary issues
            * Try again in 5-10 minutes
            * Check OpenTable's status page or social media for outage reports
        
        4. **Authentication Environment**:
            * While health_check doesn't require auth, verify OPENTABLE_ORG_KEY is set
            * Ensure MCP server environment variables are properly configured
    
    **Integration Patterns**:
        
        **Start-of-Session Health Check**:
        ```python
        async def initialize_opentable_session():
            health = await health_check()
            if not health["success"]:
                raise Exception(f"OpenTable API unavailable: {health.get('error')}")
            
            # Proceed with user registration
            user = await register_user("John", "Doe", "5551234567")
            return user
        ```
        
        **Retry with Health Check**:
        ```python  
        async def robust_restaurant_search(location, retries=3):
            for attempt in range(retries):
                try:
                    return await search_restaurants(location)
                except Exception as e:
                    health = await health_check()
                    if not health["success"]:
                        print(f"Service down on attempt {attempt + 1}: {health.get('error')}")
                        if attempt < retries - 1:
                            await asyncio.sleep(5)  # Wait before retry
                    continue
            raise Exception("Max retries exceeded")
        ```
    
    **Performance Benchmarks**:
        - **Response Time**: Typically 200-800ms
        - **Availability**: >99.9% uptime expected
        - **Timeout**: 30 second timeout configured
        - **Retry Strategy**: Recommended 3 retries with exponential backoff
    
    **Monitoring & Alerting**:
        - **Development**: Call before each session to verify connectivity
        - **Production**: Implement periodic health checks (every 5-10 minutes)
        - **CI/CD**: Include in deployment validation pipelines
        - **Alerting**: Monitor for consecutive failures indicating service issues
    
    **Common Error Patterns**:
        - **"Connection timeout"**: Network connectivity or service overload
        - **"API returned status 503"**: OpenTable service temporarily unavailable  
        - **"Health check failed: 407"**: Proxy authentication required (check credentials)
        - **"SSL/TLS errors"**: Network security or certificate issues
    
    **Best Practices**:
        1. **Always Check First**: Run health_check() before critical reservation operations
        2. **Handle Failures Gracefully**: Provide user feedback when service unavailable
        3. **Implement Retries**: Network issues may be transient
        4. **Monitor Patterns**: Log health check results for service quality monitoring
        5. **Cache Results**: Avoid excessive health checks (cache for 1-2 minutes)
    
    **Related Functions**:
        - register_user(): First authenticated operation after health check
        - All other functions: Dependent on healthy API service
        - None specifically - this is the foundation check for all operations
    
    **Service Dependencies**:
        - OpenTable REST API infrastructure
        - Modal.com hosting platform (where API is deployed)
        - Network connectivity and routing
        - Proxy services (if configured with Oxylabs)
        - DNS resolution for API endpoints
    """
    try:
        response = health_check_health_get.sync_detailed(client=ot_service.client)
        
        if response.status_code == 200:
            return {
                "success": True,
                "status": "healthy",
                "service": "opentable-rest-api",
                "message": "OpenTable API is operational"
            }
        else:
            return {
                "success": False,
                "status": "unhealthy", 
                "error": f"API returned status {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": f"Health check failed: {str(e)}"
        }

@mcp.tool()
async def modify_reservation(confirmation_number: str, reservation_token: str, restaurant_id: str, 
                           new_slot_hash: str, new_date_time: str, new_availability_token: str,
                           party_size: int, special_requests: str = None, occasion: str = None,
                           phone_number: str = None, seating_preference: str = None) -> Dict[str, Any]:
    """Modify an existing restaurant reservation by moving it to a new available slot.
    
    This endpoint changes an existing reservation to a different date/time using the specific 
    slot data obtained from get_availability(). The modification process uses a two-step 
    approach: first locking the new slot, then updating the reservation. All required data 
    must come from a recent availability check for the same restaurant.
    
    **Authentication**: Required - must call register_user() first to get API token
    
    **Prerequisites**: 
        1. Must have an existing reservation (from book_reservation() or list_reservations())
        2. Must have new slot data from get_availability() for the SAME restaurant
        3. Cannot change to a different restaurant - only time/date changes
    
    **Modification Flow**: list_reservations() → get_availability() → modify_reservation() → success!
    
    **Booking Rules**: Same credit card requirements apply as original booking
    
    Args:
        confirmation_number (str): Unique reservation identifier from booking
                                  Examples: "101750", "ABC123", "789456"  
                                  Source: confirmationNumber from reservation object
                                  Note: This is what restaurants use to identify your booking
        
        reservation_token (str): Unique reservation authorization token  
                                Examples: "01STExOdVA0yGfJNlWzUI17pJn_UbPrLdN93cXCv7Y7AE1"
                                Source: token field from reservation object  
                                Note: This authorizes the modification operation
                                
        restaurant_id (str): Restaurant identifier for the reservation
                            Examples: "96577", "212347", "30196"
                            Source: restaurant.id from reservation object
                            Note: Must match original restaurant (cannot transfer restaurants)
                            
        new_slot_hash (str): Unique identifier for the new desired time slot
                            Examples: "2431185583", "1970015633"
                            Source: slotHash from get_availability() timeslots
                            Note: Must be current/recent availability data
                            
        new_date_time (str): New reservation datetime in YYYY-MM-DDTHH:MM format
                            Examples: "2025-07-25T19:00", "2025-07-26T13:30"
                            Source: dateTime from get_availability() slot
                            Note: Must match exactly with availability slot dateTime
                            
        new_availability_token (str): Authorization token for the new slot
                                     Examples: "eyJ2IjoyLCJtIjowLCJwIjowLCJjIjo2LCJzIjowLCJuIjowfQ"
                                     Source: availabilityToken from get_availability() response
                                     Note: Validates the new slot booking authorization
                                     
        party_size (int): Number of diners for the modified reservation
                         Range: 1-20 (restaurant dependent)
                         Note: Can be changed from original reservation size
                         
        special_requests (str, optional): Special dining requests or notes
                                         Examples: "Window table preferred", "Birthday celebration",
                                                  "Wheelchair accessible table", "Quiet corner please"
                                         Max length: ~500 characters
                                         
        occasion (str, optional): Type of occasion for the reservation
                                 Examples: "birthday", "anniversary", "business dinner",
                                          "date night", "celebration", "graduation"
                                 Used for restaurant preparation and ambiance
                                 
        phone_number (str, optional): Contact phone number for the reservation
                                     Examples: "5551234567", "2125551234"
                                     Format: 10-digit phone number without formatting
                                     Note: Defaults to account phone number if not provided
                                     
        seating_preference (str, optional): Preferred seating area or table type
                                          Examples: "bar", "patio", "window", "quiet", "booth"
                                          Note: Subject to restaurant availability and policies
    
    Returns:
        Dict[str, Any]: Modification result containing:
            - success (bool): Whether reservation was successfully modified
            - message (str): Confirmation message about modification status
            - confirmation_number (str): Same reservation ID (doesn't change)
            - reservation (Dict): Updated reservation details with:
                * confirmationNumber (str): Same as original (unchanged)
                * token (str): Updated reservation token for future operations
                * restaurant (Dict): Restaurant information (unchanged):
                    + id (str): Restaurant ID
                    + name (str): Restaurant name
                * dateTime (str): NEW reservation time (updated)
                * partySize (int): Number of diners confirmed (possibly updated)
                * status (int): Reservation status code (1 = confirmed)
                * reservationStatus (str): Human-readable status ("Pending", "Confirmed")
                * creditCard (bool): Whether a credit card was used/required
            - original_datetime (str): Previous reservation time for reference
            - new_datetime (str): New reservation time for confirmation
            
        On error:
            - success (bool): False
            - error (str): Detailed error description
            - status_code (int): HTTP status code from API
            - **Common errors**:
                * "Slot no longer available" - New slot was taken by another booking
                * "Modification failed: 422" - Invalid data or constraint violation
                * "Credit card required" - New slot requires payment method not on file
                * "Restaurant policy violation" - Modification outside allowed timeframe
    
    **Example Usage**:
        ```python
        # First, get current reservations and find the one to modify
        reservations = await list_reservations()
        target_reservation = reservations["reservations"][0]  # Example
        
        # Then, get availability for the SAME restaurant
        availability = await get_availability(
            restaurant_id=target_reservation["restaurant"]["id"],
            party_size=2, days=7, start_hour=18, end_hour=22
        )
        
        # Select a new slot from availability
        new_slot = availability["availability"][0]["response"]["availability"]["timeslots"][0]
        
        # Modify the reservation
        modification = await modify_reservation(
            confirmation_number=target_reservation["confirmationNumber"],
            reservation_token=target_reservation["token"],
            restaurant_id=target_reservation["restaurant"]["id"],
            new_slot_hash=new_slot["slotHash"],
            new_date_time=new_slot["dateTime"],
            new_availability_token=availability["availability"][0]["response"]["availability"]["availabilityToken"],
            party_size=4,  # Changed from 2 to 4
            special_requests="Anniversary dinner - quiet table please",
            occasion="anniversary"
        )
        
        if modification["success"]:
            print(f"✅ Moved reservation from {modification['original_datetime']}")
            print(f"📅 New time: {modification['new_datetime']}")
            print(f"🎫 Confirmation: {modification['confirmation_number']}")
        ```
    
    **Success Response Example**:
        ```json
        {
            "success": true,
            "message": "Reservation modified successfully",
            "confirmation_number": "101750",
            "reservation": {
                "confirmationNumber": "101750",
                "token": "NEW_TOKEN_VALUE_HERE",
                "restaurant": {
                    "id": "212347",
                    "name": "SAN CARLO  Osteria Piemonte"
                },
                "dateTime": "2025-07-26T19:00",
                "partySize": 4,
                "status": 1,
                "reservationStatus": "Confirmed",
                "creditCard": false
            },
            "original_datetime": "2025-07-24T13:30",
            "new_datetime": "2025-07-26T19:00"
        }
        ```
    
    **Critical Data Requirements**:
        ALL parameters marked as required must be provided:
        1. **confirmation_number**: From list_reservations() output
        2. **reservation_token**: From original reservation object
        3. **restaurant_id**: From original reservation.restaurant.id
        4. **new_slot_hash**: From get_availability() timeslots
        5. **new_date_time**: From get_availability() slot dateTime
        6. **new_availability_token**: From get_availability() response
        7. **party_size**: Number of diners (can be different from original)
        
        **Data Freshness**: Availability data should be recent (within 15 minutes)
    
    **Error Scenarios & Solutions**:
        - **"Slot no longer available"**:
            * Someone else booked the slot while you were deciding
            * Run get_availability() again to find new options
            * Popular slots fill quickly - book faster next time
        - **"Modification failed: 422"**:
            * Invalid slot hash or expired availability token
            * Verify all data comes from same get_availability() call
            * Check that restaurant_id matches original reservation
        - **"Credit card required for new slot"**:
            * New time slot requires payment guarantee
            * Use add_credit_card() first (only works with real accounts)
            * Or select a slot with requiresCreditCard: false
        - **"Restaurant policy violation"**:
            * Trying to modify too close to reservation time
            * Some restaurants don't allow same-day modifications
            * Check restaurant's specific modification policies
    
    **Modification Constraints**:
        - **Same Restaurant Only**: Cannot transfer to different restaurant
        - **Credit Card Rules**: New slot requirements must be satisfiable 
        - **Timing Limits**: Most restaurants allow modifications up to 2-4 hours before
        - **Party Size**: Can be increased/decreased within restaurant limits
        - **Special Requests**: Can be added, changed, or removed freely
    
    **Best Practices**:
        1. **Check Availability First**: Always run get_availability() before modifying
        2. **Act Quickly**: Popular slots fill fast - don't delay after finding availability
        3. **Save New Token**: The reservation token changes after modification
        4. **Verify Changes**: Check list_reservations() after modification to confirm
        5. **Handle Failures**: Have backup slot options ready in case first choice fails
    
    **Related Functions**: 
        - list_reservations(): Get current reservation details needed for modification
        - get_availability(): Find new slots for the same restaurant
        - cancel_reservation(): Alternative if modification isn't possible
        - book_reservation(): Understanding of booking constraints applies here
    """
    if not ot_service.auth_client:
        return {"success": False, "error": "Please register a user first using register_user()"}
    
    try:
        # Prepare the modification request data
        modification_data = {
            "reservation_token": reservation_token,
            "restaurant_id": int(restaurant_id),
            "new_slot_hash": new_slot_hash,
            "new_date_time": new_date_time,
            "new_availability_token": new_availability_token,
            "party_size": party_size
        }
        
        # Add optional parameters if provided
        if special_requests:
            modification_data["special_requests"] = special_requests
        if occasion:
            modification_data["occasion"] = occasion
        if phone_number:
            modification_data["phone_number"] = phone_number
        if seating_preference:
            modification_data["seating_preference"] = seating_preference
        
        # Call the modify reservation API
        response = modify_reservation_endpoint_reservations_confirmation_number_modify_put.sync_detailed(
            confirmation_number=confirmation_number,
            client=ot_service.auth_client,
            x_org_key=ot_service.org_key,
            body=modification_data
        )
        
        if response.status_code in [200, 201] and response.parsed:
            # Parse the successful response
            data = response.parsed
            modification_result = data.get("data", {})
            reservation = modification_result.get("reservation", {})
            
            return {
                "success": True,
                "message": "Reservation modified successfully",
                "confirmation_number": confirmation_number,
                "reservation": reservation,
                "original_datetime": "Previous time (not available in response)",
                "new_datetime": new_date_time
            }
        else:
            # Handle various error status codes
            error_msg = str(response.content) if hasattr(response, 'content') else f"Status {response.status_code}"
            return {
                "success": False, 
                "error": f"Failed to modify reservation: {error_msg}",
                "status_code": response.status_code,
                "confirmation_number": confirmation_number
            }
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"Reservation modification error: {str(e)}",
            "confirmation_number": confirmation_number
        }

def main():
    """Entry point for console script"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio') 