# SHS Voice AI Agent

AI-powered voice support system for appliance troubleshooting and technician scheduling.

This project simulates a real-world customer support workflow where users can call a phone number, describe appliance issues using natural language, receive troubleshooting guidance, and schedule technician appointments through an AI-driven conversational system.

The system integrates:
- Twilio Voice APIs
- OpenAI LLM orchestration
- FastAPI backend services
- PostgreSQL persistence
- Docker Compose deployment
- SMS appointment confirmations

---

## Key Features

- AI-driven voice troubleshooting
- Stateful conversation orchestration
- Dynamic technician scheduling
- PostgreSQL-backed persistence
- SMS booking confirmation
- Dockerized local deployment
- Twilio phone integration
- Multi-step conversational workflows

## Architecture Diagram

```text
                ┌─────────────────────┐
                │ Customer Phone Call │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │       Twilio        │
                │ Voice + Speech-to-Text
                └──────────┬──────────┘
                           │ Webhooks
                           ▼
                ┌─────────────────────┐
                │      ngrok Tunnel   │
                └──────────┬──────────┘
                           │
                           ▼
          ┌─────────────────────────────────┐
          │        FastAPI Backend          │
          │                                 │
          │  - Voice Webhook Handling       │
          │  - AI Orchestration             │
          │  - Conversation State Machine   │
          │  - Scheduling Workflow          │
          │  - SMS Notifications            │
          └──────────┬──────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼

┌────────────┐ ┌────────────┐ ┌──────────────┐
│   OpenAI   │ │ PostgreSQL │ │    Twilio    │
│ Reasoning  │ │ Persistence│ │ SMS Delivery │
└────────────┘ └────────────┘ └──────────────┘
```

## Conversational Workflow

Example customer flow:

1. Customer calls Twilio phone number
2. AI asks for appliance issue
3. AI collects zip code
4. AI provides troubleshooting guidance
5. AI asks whether issue was resolved
6. If unresolved, AI offers technician scheduling
7. AI finds available technician slot
8. Customer confirms booking
9. AI books appointment
10. SMS confirmation is sent to customer

## Tech Stack

### Backend
- FastAPI
- Python 3.11
- SQLAlchemy

### AI / LLM
- OpenAI GPT-4o-mini

### Voice Infrastructure
- Twilio Voice
- Twilio Speech-to-Text
- Twilio SMS

### Database
- PostgreSQL

### Containerization
- Docker
- Docker Compose

### Local Development
- ngrok

## Design Decisions

### Deterministic Conversation State Machine

Initially, the conversational flow was fully controlled by the LLM. This caused repeated troubleshooting loops and inconsistent scheduling transitions.

To improve reliability, the final implementation uses a deterministic state-machine approach where:
- application logic controls workflow transitions
- the LLM is used primarily for extraction and conversational responses

This design improves:
- conversational consistency
- debugging
- predictability
- production reliability

---

### Separation of Concerns

The system separates:
- voice transport (Twilio)
- orchestration logic
- AI reasoning
- scheduling logic
- notification delivery
- persistence

This keeps the architecture modular and easier to extend.

---

### PostgreSQL over SQLite

The final implementation uses PostgreSQL to better simulate production deployment environments and support multi-container orchestration through Docker Compose.

---

### Dockerized Deployment

The backend and PostgreSQL database are containerized to provide:
- reproducible local development
- isolated dependencies
- easier onboarding
- deployment portability

## Local Setup

### 1. Clone Repository

```bash
git clone <repo_url>
cd shs-voice-ai-agent
```

### 2. Configure Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

DATABASE_URL=postgresql://shs_user:shs_password@db:5432/shs_voice_agent
```

### 3. Start Services

```bash
docker compose up --build
```

### 4. Start ngrok

```bash
ngrok http 8000
```

### 5. Configure Twilio Webhook

Configure incoming voice webhook:

```text
https://<ngrok-url>/twilio/voice
```

### 6. Test Voice Workflow

Call the Twilio phone number and follow the conversational flow.

## Example Interaction

Customer:
> My washer is leaking.

AI:
> What is the zip code where the appliance is located?

Customer:
> 95112

AI:
> Please check whether the inlet hoses are tightly connected. Did this solve the issue?

Customer:
> No, it is still leaking.

AI:
> Would you like me to schedule a technician appointment?

Customer:
> Yes.

AI:
> I found an available technician appointment on May 16 at 10:00 AM. Would you like to confirm this booking?

Customer:
> Yes confirm booking.

AI:
> Your technician appointment has been successfully booked.

## Future Improvements

- Real-time streaming voice responses
- Retrieval-Augmented Generation (RAG) for appliance manuals
- Multi-language support
- Authentication and customer accounts
- Calendar integrations
- Human escalation workflows
- Production-grade observability and tracing
- Kubernetes deployment

## Notes

This project was designed to simulate a production-style AI voice support workflow while maintaining simplicity for local development and evaluation.

The implementation prioritizes:
- reliability
- deterministic orchestration
- modular backend architecture
- realistic customer support workflows