from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.database import get_db
from app.services.agent_orchestration_service import process_customer_message_logic


router = APIRouter()


@router.post("/twilio/voice")
async def inbound_voice_call():
    voice_response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/twilio/process-speech",
        method="POST",
        speech_timeout="2",
        timeout="6",
    )

    gather.say(
        "Hello, thank you for calling Sears Home Services. "
        "Please tell me the appliance and the issue. "
        "For example, my washer is leaking in zip code 95112."
    )

    voice_response.append(gather)

    voice_response.say(
        "I did not hear anything. Please call again when you are ready."
    )
    voice_response.hangup()

    return Response(
        content=str(voice_response),
        media_type="application/xml",
    )


@router.post("/twilio/process-speech")
async def process_speech_from_twilio(
    SpeechResult: str = Form(default=""),
    CallSid: str = Form(default="demo-call"),
    From: str = Form(default=""),
    db: Session = Depends(get_db),
):
    voice_response = VoiceResponse()

    cleaned_speech = SpeechResult.strip()

    if not cleaned_speech:
        gather = Gather(
            input="speech",
            action="/twilio/process-speech",
            method="POST",
            speech_timeout="2",
            timeout="6",
        )

        gather.say(
            "Sorry, I did not catch that. Please repeat the appliance and issue."
        )

        voice_response.append(gather)

        voice_response.say("I still did not hear anything. Goodbye.")
        voice_response.hangup()

        return Response(
            content=str(voice_response),
            media_type="application/xml",
        )

    agent_result = await process_customer_message_logic(
        payload={
            "call_sid": CallSid,
            "message": cleaned_speech,
            "customer_phone": From,
        },
        db=db,
    )

    assistant_response = agent_result["assistant_response"]
    intent = agent_result.get("intent")

    if intent in ["confirmation", "emergency"]:
        voice_response.say(assistant_response)
        voice_response.say("Thank you for calling Sears Home Services. Goodbye.")
        voice_response.hangup()

    else:
        gather = Gather(
            input="speech",
            action="/twilio/process-speech",
            method="POST",
            speech_timeout="2",
            timeout="8",
        )

        gather.say(assistant_response)

        voice_response.append(gather)

        voice_response.say(
            "I did not hear anything further. Thank you for calling Sears Home Services. Goodbye."
        )
        voice_response.hangup()

    return Response(
        content=str(voice_response),
        media_type="application/xml",
    )