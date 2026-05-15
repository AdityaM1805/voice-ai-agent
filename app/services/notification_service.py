from twilio.rest import Client

from app.config import settings


def send_booking_confirmation_sms(
    to_phone_number: str,
    appointment_id: int,
):
    """
    Sends SMS confirmation after appointment booking.

    Twilio sends the message from our configured Twilio phone number.
    """

    if not to_phone_number:
        return None

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    message = client.messages.create(
        body=(
            f"Your Sears Home Services appointment is confirmed. "
            f"Appointment ID: {appointment_id}."
        ),
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_phone_number,
    )

    return message.sid