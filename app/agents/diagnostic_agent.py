import json

from openai import OpenAI

from app.config import settings
from app.prompts.system_prompt import DIAGNOSTIC_AGENT_SYSTEM_PROMPT


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def detect_customer_intent(user_message: str) -> str:
    """
    Detect the customer's high-level intent.

    This function returns one label:
    troubleshooting, scheduling, confirmation, emergency, or general.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are an intent classification assistant.

Your job is to classify customer intent.

Return ONLY one of these labels:
- troubleshooting
- scheduling
- confirmation
- emergency
- general

Intent definitions:

troubleshooting:
- describing appliance problem
- asking why appliance is failing
- discussing symptoms

scheduling:
- requesting technician visit
- asking for service appointment
- wanting available appointment slots

confirmation:
- explicitly confirming a previously offered appointment
- accepting a proposed booking
- agreeing to finalize scheduling

emergency:
- smoke
- sparks
- burning smell
- gas leak
- electrical hazard

general:
- greetings
- unrelated discussion

IMPORTANT:
If the customer is agreeing to finalize or confirm an already offered appointment,
ALWAYS return:
confirmation

Examples:

"My washer leaks water"
→ troubleshooting

"I need a technician"
→ scheduling

"Book service for tomorrow"
→ scheduling

"Yes confirm booking"
→ confirmation

"Yes please schedule it"
→ confirmation

"That slot works for me"
→ confirmation

"I smell smoke from my dryer"
→ emergency
""",
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip().lower()


def generate_diagnostic_response(
    user_message: str,
    conversation_context: dict,
) -> str:
    """
    Generate a short, voice-friendly diagnostic response.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": DIAGNOSTIC_AGENT_SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": f"Known conversation context: {conversation_context}",
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=settings.OPENAI_TEMPERATURE,
    )

    return response.choices[0].message.content


def extract_structured_information(user_message: str) -> dict:
    """
    Extract structured appliance information from customer message.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Extract structured appliance support information.

Return ONLY valid JSON.

Fields:
- appliance_type
- zip_code
- symptoms

If a field is missing, return null.

Example:
{
  "appliance_type": "washer",
  "zip_code": "95112",
  "symptoms": "water leaking from bottom"
}
""",
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    try:
        parsed_content = json.loads(content)
        if not isinstance(parsed_content, dict):
            return {}
        return parsed_content
    except Exception:
        return {}