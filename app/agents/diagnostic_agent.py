from openai import OpenAI

from app.config import settings
from app.prompts.system_prompt import DIAGNOSTIC_AGENT_SYSTEM_PROMPT


# Create OpenAI client using API key from environment config.
# We do not hardcode the key because secrets should never live in source code.
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_diagnostic_response(
    user_message: str,
    conversation_context: dict,
) -> str:
    """
    Generate the next assistant response for the appliance diagnostic call.

    Parameters:
    - user_message: latest thing the customer said
    - conversation_context: information already collected in the call

    Example context:
    {
        "appliance_type": "washer",
        "symptoms": "not draining",
        "zip_code": "95112"
    }

    Returns:
    - short voice-friendly assistant response
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