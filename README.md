# AI Voice Service

A real-time, multimodal AI voice agent built with **FastAPI**, **Pipecat**, **Twilio Media Streams**, and **Google Gemini Live**.

This service allows users to call a phone number (or initiate a call via the web UI) and have a natural, low-latency conversation with an AI assistant. The AI can be configured with different "personas" to act as a veterinary receptionist, customer support agent, or any other role.

## Key Features

-   **Real-time Voice Conversation**: Bidirectional audio streaming with low latency.
-   **Multimodal Intelligence**: Powered by `gemini-2.5-flash-native-audio-preview` for understanding tone and nuance.
-   **Telephony Integration**: Uses Twilio Media Streams to connect phone calls to the AI via WebSockets.
-   **Pipecat Pipeline**: Robust frame-based processing for audio, text, and LLM interactions.
-   **Configurable Personas**: Easily switch between different system instructions and voice settings.
-   **Docker Ready**: simple containerization for deployment.

## Architecture

The system follows an MVC-like structure within a FastAPI application:

-   **Frontend**: Simple HTML/JS interface to initiate calls.
-   **Backend (FastAPI)**:
    -   `/`: Serves the web UI.
    -   `/api/personas`: Lists available AI personas.
    -   `/call`: Initiates an outbound call via Twilio.
    -   `/twiml`: Generates TwiML instructions for Twilio to connect the call to the WebSocket.
    -   `/ws`: WebSocket endpoint that handles the real-time audio stream (Twilio <-> Pipecat <-> Gemini).

## Prerequisites

-   **Python 3.11+**
-   **uv** (Python package manager)
-   **Twilio Account**: You need an Account SID, Auth Token, and a purchased phone number.
-   **Google Cloud Project**: With Gemini API access enabled.
-   **ngrok** (for local development): To expose your local server to Twilio.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd AI-Voice-Service
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory (copy from `.env.example` if available).

    **`.env` Configuration:**
    ```ini
    # Server Configuration
    PORT=8520
    ENV=development
    DOMAIN=https://your-ngrok-url.ngrok-free.app  # Must be HTTPS

    # Google / Gemini
    GOOGLE_API_KEY=your_google_api_key

    # Twilio Credentials
    TWILIO_ACCOUNT_SID=your_twilio_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio number
    ```
    > **Note:** `DOMAIN` must be the public URL of your server (e.g., from ngrok). Do not use `localhost`.

## Usage

### 1. Start Support Tunnel (ngrok)
Twilio needs to reach your local server.
```bash
ngrok http 8520
```
Copy the forwarding URL (e.g., `https://c95d-123-45.ngrok-free.app`) and set it as the `DOMAIN` in your `.env` file.

### 2. Run the Application

**Locally:**
```bash
uv run python main.py
```
The server will start on `http://0.0.0.0:8520`.

**With Docker:**
```bash
# Build
docker build -t ai-voice-service .

# Run
docker run -p 8520:8520 --env-file .env ai-voice-service
```

### 3. Making Calls

#### Via Web UI
1.  Open `http://localhost:8520` in your browser.
2.  Select a **Persona** (e.g., "Phone Doctor").
3.  Enter the **Phone Number** you want to call.
4.  Click **Call**. The phone will ring, and upon answering, the AI will start speaking.

#### Via Inbound Call
Configure your Twilio Phone Number's Voice URL to point to your server's TwiML endpoint:
`https://your-ngrok-url.ngrok-free.app/twiml?persona_id=vet_care_assistant`

When you call your Twilio number, it will connect to the AI.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web Interface |
| `GET` | `/api/personas` | List available personas |
| `POST` | `/call` | Trigger an outbound call. JSON body: `{"persona_id": "...", "phone_number": "..."}` |
| `POST` | `/twiml` | Twilio webhook. Returns TwiML XML. Query param: `persona_id` |
| `WS` | `/ws` | WebSocket for audio streaming |

## Project Structure

```
app/
├── main.py              # Application entry point
├── config.py            # Configuration loader
├── models/              # Data models (Personas)
├── services/            # Business Logic
│   ├── bot_service.py      # Pipecat + Gemini pipeline
│   └── twilio_service.py   # Twilio API interactions
├── controllers/         # Route Handlers
│   ├── api_controller.py   # REST API
│   ├── twiml_controller.py # Twilio Webhooks
│   ├── web_controller.py   # Frontend serving
│   └── websocket_controller.py # Audio streaming
└── views/               # HTML Templates
```
