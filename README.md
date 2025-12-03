# Text-to-LLM Telegram Bot

A FastAPI backend that connects Telegram users to LLM providers using a Telegram bot webhook.  
This README documents the exact setup our group used for running the project locally during development.

## Group Members:
- **Samuel Vekovius (vekoLSU)**
- **Caleb Wycoff (crusewycoff1)**
- **Tobias Hill (RealTobiasHill)**
- **Jaroslav Aupart (YSLja)**
- **Michael Meyers (Chog7)**

## Architecture
```
User → Telegram Bot → FastAPI Server (/webhook) → LLM API → FastAPI Server → Telegram Bot → User
```
## Features

- **Multi-Provider Support**: Easily switch between OpenAI, Anthropic, and xAI
- **Webhook-Based**: Real-time Telegram message processing
- **Config-Driven**: Uses `.env` for all secrets and configuration
- **Modular Design**: Separate controller, service, and config layers
- **Local-Friendly**: Designed to run on a laptop with `uvicorn` + `ngrok`

## Project Structure

```
/project-root
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server with /webhook and /set-webhook endpoints
│   ├── config.py                # Environment variable configuration and validation
│   ├── telegram_controller.py   # Telegram API interactions
│   ├── llm_service.py           # LLM provider integrations
│   ├── models/
│   │   ├── __init__.py
│   │   └── message.py           # Pydantic models
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Logging utilities
│
├── requirements.txt
├── README.md
└── .env                         # Created manually in the project root
```

## Setup Instructions (for my group members)

### 1. Prerequisites

- Python 3.13 (important; newer versions like 3.14 can cause dependency issues)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- LLM API Key (OpenAI, Anthropic, or xAI)
- `ngrok` installed and configured

### 2. Installation

Clone the repository:
```bash
git clone https://github.com/vekoLSU/Text-to-LLM-CSC4330.git
cd Text-to-LLM-CSC4330
```

Create and activate a virtual environment using Python 3.13:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=gpt-4o-mini

# Server Configuration
HOST=0.0.0.0
PORT=8000
MAX_TOKENS=1000
DEBUG=False
```

#### Supported Models

**OpenAI:**
- `gpt-4o-mini` (recommended for cost efficiency)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Anthropic:**
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**xAI:**
- `grok-beta`

### 4. Getting API Keys

**Telegram Bot Token:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token provided

**OpenAI API Key:**
- Get it from: https://platform.openai.com/api-keys

**Anthropic API Key:**
- Get it from: https://console.anthropic.com/settings/keys

**xAI API Key:**
- Get it from: https://console.x.ai/

## Running the Server

### Local Development

Start the FastAPI server with auto-reload:

```bash
uvicorn app.main:app --reload
```

The server will start at:

```
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "healthy"}
```

## Setting Up Telegram Webhook (Local with ngrok)

To let Telegram reach your local server, use ngrok to expose port 8000.

### 1. Start ngrok

In a new terminal (leave uvicorn running in the first one):

```bash
ngrok http 8000
```

You will see a forwarding URL like:

```
Forwarding  https://example-url.ngrok-free.dev -> http://localhost:8000
```

Copy the HTTPS URL.

### 2. Set webhook using the FastAPI helper endpoint

In another terminal, run:

```bash
curl -X POST "https://example-url.ngrok-free.dev/set-webhook" \
  -H "Content-Type: application/json" \
  -d "{\"webhook_url\": \"https://example-url.ngrok-free.dev/webhook\"}"
```

You should see a JSON response indicating the webhook was set.

### 3. Verify Webhook Status (optional)

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Replace `<YOUR_BOT_TOKEN>` with your actual bot token.

## Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy"}
```

### 2. Test with Telegram

1. Open Telegram and find your bot via its username
2. Send it a simple message, for example:

```
hello
```

3. Check:
   - The uvicorn terminal for `/webhook` logs
   - The ngrok terminal for incoming requests

If everything is configured correctly, the bot will reply using the configured LLM provider.

## Switching LLM Providers

To switch between providers, update your `.env` file and restart the server.

**For OpenAI:**

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

**For Anthropic:**

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022
```

**For xAI:**

```env
LLM_PROVIDER=xai
LLM_API_KEY=xai-...
LLM_MODEL=grok-beta
```

Then restart the server:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### `GET /`

Basic service info / ping.

### `GET /health`

Simple health check endpoint.

### `POST /webhook`

Main webhook endpoint for Telegram updates.

### `POST /set-webhook`

Helper endpoint to programmatically set the Telegram webhook.

**Request:**

```json
{
  "webhook_url": "https://your-public-url/webhook"
}
```

## Logging

Logs are output to stdout with the format:

```
2025-11-15 15:02:03 - text-to-llm - INFO - Message received from chat 123456
```

To view logs in real-time:

```bash
uvicorn app.main:app --reload | tee bot.log
```

## Troubleshooting

### Bot not responding

1. Check that uvicorn is running without errors.
2. Ensure ngrok is running and the webhook was set with the current ngrok URL.
3. Check webhook info:

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

4. Verify `.env` has valid values for:
   - `TELEGRAM_BOT_TOKEN`
   - `LLM_API_KEY`
   - `LLM_PROVIDER`
   - `LLM_MODEL`

### Server won't start

- Ensure the virtual environment is active
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` exists and is correctly filled
- Confirm Python version is 3.13

## Contributing

To contribute:
1. Create a feature branch
2. Make your changes
3. Test locally
4. Create a pull request and send a message in the Discord

## License

None
