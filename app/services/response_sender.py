import httpx
import os

from app.services.inference import generate_response
from app.core.logger import logger

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")


async def process_test_message(user_message: str):
    try:
        llm_response = await generate_response(user_message)
        logger.info(f"Response for test:\n{llm_response}")
        return llm_response
    except Exception:
        logger.exception("Error sending WhatsApp response.")


async def process_whatsapp_message(user_message: str, customer_telephone: str, phone_number_id: str):
    try:
        llm_response = await generate_response(user_message, customer_telephone)
        logger.info(f"Response for {customer_telephone}:\n{llm_response}")
        await send_whatsapp_message(phone_number_id, customer_telephone, llm_response)
    except Exception:
        logger.exception("Error sending WhatsApp response.")


async def send_whatsapp_message(phone_number_id: str, to_number: str, message: str):
    url = f"https://graph.facebook.com/v23.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    logger.debug(f"Payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            logger.info(f"Error {response.status_code} en el envío: {response.text}")
            if response.status_code == 401:
                data = response.json()
                if data.get("error", {}).get("code") == 190:
                    logger.error("El token de acceso ha expirado. Debes renovarlo.")

        return response.json()
