import requests
import os

from typing import Dict, Any

from app.core.logger import logger

def submit_google_form(name: str, email: str, profession: str) -> None:
    """
    Submits a Google Form with predefined data.
    """
    FORM_ULR = "https://docs.google.com/forms/d/e/1FAIpQLSc2XWE-yvyQJj8s4Kh8OYvIVBFhrrU2z-vjEwcJiFno3cK8ow/formResponse"

    form_data = {
        "entry.1554944402": name,        # name
        "entry.662612736": email,  # email
        "entry.1844920426": profession[0].upper()+profession[1:]         # profession (must match dropdown option)
    }
    headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
    
    logger.debug(f"Submitting form with data: {form_data}")
    
    # Send the POST request
    response = requests.post(FORM_ULR, data=form_data, headers=headers)

    # Optional: Check if it worked
    if response.status_code == 200:
        logger.debug("Form submitted successfully.")
        return True
    else:
        logger.debug(f"Form submission failed. Status code: {response.status_code}")
        return False
    


GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")

def create_or_update_contact(api_key: str, location_id: str, name: str, profession: str, email: str, phone: str):
    """
    Creates or updates a contact in Go High Level (GHL).

    Args:
        api_key (str): Your GHL API key (Agency or Location API Key).
        location_id (str): The GHL Location ID where the contact will be added.
        name (str): Full name of the contact.
        profession (str): Profession (stored as a custom field).
        email (str): Email address.
        phone (str): Phone number (include country code if needed).

    Returns:
        dict: Response JSON from the GHL API.
    """
    url = "https://rest.gohighlevel.com/v1/contacts/"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "locationId": location_id,
        "name": name,
        "email": email,
        "phone": phone,
        "customField": {
            "uv2ZiD8sD3nbLMM22Xt3": profession  # You'll need to use the custom field ID here.
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

async def submit_contact_node(state: Dict[str, Any], config) -> Dict[str, Any]:
     # Extract current known values from state
    name = state.get("customer_name")
    profession = state.get("customer_profession")
    email = state.get("customer_email")
    phone = state.get("customer_phone_number", None)
    success = False
    if name and profession and email:
        if state['form_submitted'] is False:
            success = submit_google_form(name=name, email=email, profession=profession)
            logger.debug(f"Form submission success: {success}")
            contact = create_or_update_contact(
            api_key=GHL_API_KEY,
            location_id=GHL_LOCATION_ID,
            name=name,
            profession=profession,  # Ensure it's matched to a valid custom field
            email=email,
            phone=phone
        )
            logger.debug(f"Contact created/updated: {contact}")

    
    form_submitted = state.get("form_submitted", False) or success
    return {'form_submitted': form_submitted}