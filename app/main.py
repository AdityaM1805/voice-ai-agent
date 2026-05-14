from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.services.scheduling_service import find_available_slots 
from app.agents.diagnostic_agent import generate_diagnostic_response

#create FastAPI application instance
app = FastAPI(
    title="SHS Voice AI Agent",
    version="1.0.0",
)

#simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy",
            "service": "SHS Voice AI Agent"}

#simple endpoint to verify environment variables are loaded correctly
@app.get("/config-check")
async def config_check():
    return {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "DATABASE_URL": settings.DATABASE_URL,
        "TWILIO_ACCOUNT_SID": settings.TWILIO_ACCOUNT_SID,
        "TWILIO_AUTH_TOKEN": settings.TWILIO_AUTH_TOKEN,
        "TWILIO_PHONE_NUMBER": settings.TWILIO_PHONE_NUMBER
    }

@app.get("/test/available-slots")
async def test_available_slots(
    zip_code: str,
    appliance_type: str,
    db: Session = Depends(get_db),
):
    """
    Temporary test endpoint.

    This lets us verify scheduling logic before connecting AI.
    """

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
    """
    Temporary endpoint to test the AI diagnostic agent
    before connecting it to phone calls.
    """

    user_message = payload.get("message", "")

    conversation_context = payload.get("context", {})

    assistant_response = generate_diagnostic_response(
        user_message=user_message,
        conversation_context=conversation_context,
    )

    return {
        "assistant_response": assistant_response
    }