"""
Chapa API integration service for payment processing.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

CHAPA_API_BASE_URL = "https://api.chapa.co/v1"
CHAPA_INITIATE_URL = f"{CHAPA_API_BASE_URL}/transaction/initialize"
CHAPA_VERIFY_URL = f"{CHAPA_API_BASE_URL}/transaction/verify"


def initiate_payment(amount, email, first_name, last_name, phone, currency="ETB", tx_ref=None, callback_url=None, return_url=None, **kwargs):
    """
    Initiate a payment transaction with Chapa API.
    
    Args:
        amount: Payment amount (float or Decimal)
        email: Customer email
        first_name: Customer first name
        last_name: Customer last name
        phone: Customer phone number
        currency: Currency code (default: ETB)
        tx_ref: Transaction reference (will be generated if not provided)
        callback_url: Callback URL for webhook
        return_url: Return URL after payment
        **kwargs: Additional parameters for Chapa API
    
    Returns:
        dict: Response containing transaction_id and checkout_url, or None if failed
    """
    secret_key = getattr(settings, 'CHAPA_SECRET_KEY', '')
    
    if not secret_key:
        logger.error("CHAPA_SECRET_KEY is not configured in settings")
        return None
    
    if not tx_ref:
        import uuid
        tx_ref = f"TX-{uuid.uuid4().hex[:12].upper()}"
    
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(float(amount)),
        "currency": currency,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone,
        "tx_ref": tx_ref,
        **kwargs
    }
    
    if callback_url:
        payload["callback_url"] = callback_url
    
    if return_url:
        payload["return_url"] = return_url
    
    try:
        response = requests.post(CHAPA_INITIATE_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success" and "data" in data:
            transaction_data = data["data"]
            return {
                "transaction_id": transaction_data.get("tx_ref"),
                "checkout_url": transaction_data.get("checkout_url"),
                "status": "success",
                "message": data.get("message", "Payment initiated successfully"),
                "full_response": data
            }
        else:
            logger.error(f"Chapa API error: {data.get('message', 'Unknown error')}")
            return {
                "status": "error",
                "message": data.get("message", "Failed to initiate payment"),
                "full_response": data
            }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Chapa API: {str(e)}")
        return {
            "status": "error",
            "message": f"Network error: {str(e)}",
            "full_response": None
        }
    except Exception as e:
        logger.error(f"Unexpected error in initiate_payment: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "full_response": None
        }


def verify_payment(transaction_id):
    """
    Verify a payment transaction with Chapa API.
    
    Args:
        transaction_id: Transaction reference (tx_ref) to verify
    
    Returns:
        dict: Response containing payment status and details, or None if failed
    """
    secret_key = getattr(settings, 'CHAPA_SECRET_KEY', '')
    
    if not secret_key:
        logger.error("CHAPA_SECRET_KEY is not configured in settings")
        return None
    
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    verify_url = f"{CHAPA_VERIFY_URL}/{transaction_id}"
    
    try:
        response = requests.get(verify_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success" and "data" in data:
            transaction_data = data["data"]
            payment_status = transaction_data.get("status", "").lower()
            
            return {
                "status": "success",
                "payment_status": payment_status,
                "transaction_id": transaction_data.get("tx_ref"),
                "amount": transaction_data.get("amount"),
                "currency": transaction_data.get("currency"),
                "email": transaction_data.get("email"),
                "message": data.get("message", "Payment verified successfully"),
                "full_response": data
            }
        else:
            logger.error(f"Chapa verification error: {data.get('message', 'Unknown error')}")
            return {
                "status": "error",
                "message": data.get("message", "Failed to verify payment"),
                "full_response": data
            }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Chapa verification API: {str(e)}")
        return {
            "status": "error",
            "message": f"Network error: {str(e)}",
            "full_response": None
        }
    except Exception as e:
        logger.error(f"Unexpected error in verify_payment: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "full_response": None
        }
