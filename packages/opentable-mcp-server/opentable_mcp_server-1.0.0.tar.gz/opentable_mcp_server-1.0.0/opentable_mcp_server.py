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
    """Register a new OpenTable test user.
    
    Args:
        first_name: User's first name
        last_name: User's last name  
        phone_number: 10-digit US phone number (e.g. "5551234567")
    
    Returns:
        Dictionary with registration result including email, api_token, and user_id
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
    """Search for restaurants by location and optional filters.
    
    Args:
        location: City, address, or landmark (e.g. "New York, NY", "Vancouver, BC")
        restaurant_name: Optional restaurant name or cuisine type (e.g. "italian", "Le Bernardin")
        party_size: Number of diners (default: 2)
        max_results: Maximum restaurants to return (default: 20)
    
    Returns:
        Dictionary with list of restaurants and search metadata
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
    """Get available time slots for a restaurant.
    
    Args:
        restaurant_id: Restaurant ID from search results
        party_size: Number of diners (default: 2)
        days: Days ahead to check (default: 7)
        start_hour: Earliest hour to check in 24h format (default: 17 = 5 PM)
        end_hour: Latest hour to check in 24h format (default: 21 = 9 PM)
    
    Returns:
        Dictionary with availability information including timeslots and booking requirements
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
    """Book a restaurant reservation.
    
    Args:
        restaurant_id: Restaurant ID from search results
        slot_hash: Slot hash from availability response  
        date_time: Reservation datetime in format "YYYY-MM-DDTHH:MM"
        availability_token: Availability token from availability response
        party_size: Number of diners
        location: Location string for geocoding (e.g. "New York, NY")
        special_requests: Optional special requests or notes
        occasion: Optional occasion type (e.g. "birthday", "anniversary")
    
    Returns:
        Dictionary with booking result including confirmation number if successful
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
    """List all user reservations and profile information.
    
    Returns:
        Dictionary with user reservations and profile details
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
                    "email": data.get("email"),
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
    """Cancel a reservation.
    
    Args:
        confirmation_number: Reservation confirmation number
        restaurant_id: Restaurant ID from the reservation
        reservation_token: Reservation token from the reservation object
    
    Returns:
        Dictionary with cancellation result
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
    """Add a credit card to your OpenTable account.
    
    Note: This only works with real OpenTable accounts, not test accounts.
    
    Args:
        card_full_name: Full name as it appears on the card
        card_number: Credit card number
        card_exp_month: Expiration month (1-12)
        card_exp_year: Expiration year (YYYY)
        card_cvv: Card verification value (3-4 digits)
        card_zip: Billing ZIP code
    
    Returns:
        Dictionary with card addition result
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
async def health_check() -> Dict[str, Any]:
    """Check the health status of the OpenTable API.
    
    Returns:
        Dictionary with API health status
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

def main():
    """Entry point for console script"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio') 