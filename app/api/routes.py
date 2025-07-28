from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import os
import json

from app.services.response_sender import process_whatsapp_message, process_test_message
from app.core.logger import logger



router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

@router.get("/whatsapp")
async def verify_token(request: Request):
    logger.info("Verifying WhatsApp webhook token...")
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Invalid verification"}

@router.post("/whatsapp")
async def handle_incoming_message(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    logger.info("Received WhatsApp message payload: \n%s", json.dumps(payload, indent=2, ensure_ascii=False))
    try:
        # Get the first entry and change
        entry = payload["entry"][0]
        change = entry["changes"][0]["value"]

        # Extract metadata
        phone_number_id = change["metadata"]["phone_number_id"]
        display_phone_number = change["metadata"]["display_phone_number"]

        # Extract message details
        messages = change.get("messages")

        if not messages:
            # No hay mensaje, puede ser un estado o evento no relevante
            return {"status": "no message"}
        
        message_obj = messages[0]
        customer_telephone = message_obj["from"]
        user_message = message_obj["text"]["body"]

        # Procesar en segundo plano
        background_tasks.add_task(process_whatsapp_message, user_message, customer_telephone, phone_number_id)
        return JSONResponse(status_code=200, content={"status": "received"})

    except Exception as e:
        logger.exception("Error processing WhatsApp message.")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
@router.post("/test")
async def handle_test_message(request: Request):
    payload = await request.json()
    logger.info("Received test message payload: \n%s", json.dumps(payload, indent=2, ensure_ascii=False))
    try:
        # Extract message details
        messages = payload.get("messages")
    

        # Procesar en segundo plano
        response = await process_test_message(messages)
        return JSONResponse(status_code=200, content={"status": "received", "response": response})

    except Exception as e:
        logger.exception("Error processing Test message.")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@router.post("/test_crm")
async def handle_crm_message(request: Request):
    payload = await request.json()
    logger.info("Received test message payload: \n%s", json.dumps(payload, indent=2, ensure_ascii=False))
    try:
        message = payload.get("message").get("body")
        logger.info(f"Received test CRM message: {message}")
    except Exception as e:
        logger.exception("Error processing Test message.")
        raise HTTPException(status_code=400, detail="Internal input format")

    try:
        # Procesar en segundo plano
        response = await process_test_message(message)
        return JSONResponse(status_code=200, content={"status": "received", "response": response, "message_to_send": response})

    except Exception as e:
        logger.exception("Error processing Test message.")
        raise HTTPException(status_code=500, detail="Internal server error")