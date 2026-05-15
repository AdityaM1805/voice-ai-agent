from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.scheduling_service import find_available_slots
from app.agents.diagnostic_agent import generate_diagnostic_response
from app.services.agent_orchestration_service import process_customer_message_logic
from app.voice.twilio_routes import router as twilio_router


app = FastAPI(
    title="SHS Voice AI Agent",
    version="1.0.0",
)

app.include_router(twilio_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SHS Voice AI Agent",
    }


@app.get("/config-check")
async def config_check():
    return {
        "database_url": settings.DATABASE_URL,
        "twilio_phone_number": settings.TWILIO_PHONE_NUMBER,
    }


@app.get("/test/available-slots")
async def test_available_slots(
    zip_code: str,
    appliance_type: str,
    db: Session = Depends(get_db),
):
    slots = find_available_slots(
        db=db,
        zip_code=zip_code,
        appliance_type=appliance_type,
    )

    return [
        {
            "slot_id": slot.id,
            "technician_id": slot.technician_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        }
        for slot in slots
    ]


@app.post("/test/diagnostic-agent")
async def test_diagnostic_agent(payload: dict):
    user_message = payload.get("message", "")
    conversation_context = payload.get("context", {})

    assistant_response = generate_diagnostic_response(
        user_message=user_message,
        conversation_context=conversation_context,
    )

    return {
        "assistant_response": assistant_response,
    }


@app.post("/agent/process")
async def process_customer_message(
    payload: dict,
    db: Session = Depends(get_db),
):
    return await process_customer_message_logic(
        payload=payload,
        db=db,
    )