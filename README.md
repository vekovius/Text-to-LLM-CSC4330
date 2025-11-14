# Text-to-LLM Telegram Bot

A production-ready FastAPI backend that connects Telegram users to LLM providers.

## Group Members:
- **Samuel Vekovius (vekoLSU)**
- **Caleb Wycoff (crusewycoff1)**
- **Tobias Hill (RealTobiasHill)**
- **add ur name/gihub profile and commit**
- **add ur name/gihub profile and commit**

## Architecture

```
User → Telegram Bot → FastAPI Server (/webhook) → LLM API → FastAPI Server → Telegram Bot → User
```

## Features

- **Multi-Provider Support**: Easily switch between OpenAI, Anthropic, and xAI
- **Webhook-Based**: Efficient real-time message processing
- **Production Ready**: Includes logging, error handling, and health checks
- **Type-Safe**: Full Pydantic models for data validation
- **Easy Deployment**: Simple environment variable configuration

## Project Structure

```
/project-root
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server with /webhook endpoint
│   ├── config.py                # Environment variable configuration
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
└── .env                         # Create this from .env.example
```

## Setup Instructions (for my group members)

### 1. Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- LLM API Key (OpenAI, Anthropic, or xAI)

### 2. Installation

Clone the repository:
```bash
git clone https://github.com/vekoLSU/Text-to-LLM-CSC4330.git
cd Text-to-LLM-CSC4330
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
LLM_PROVIDER=openai          # Options: openai, anthropic, xai
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=gpt-4o-mini        # See model options below

# Server Configuration (Optional)
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

Start the server with auto-reload:
```bash
uvicorn app.main:app --reload
```

Or run directly:
```bash
python -m uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### Production

Run without reload:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Setting Up Telegram Webhook

Your server must be publicly accessible via HTTPS. Once deployed:

### Method 1: Browser (Quick)

Navigate to:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/webhook
```

Replace:
- `<YOUR_BOT_TOKEN>` with your actual bot token
- `yourdomain.com` with your server's domain

### Method 2: API Endpoint

Send a POST request to your server:
```bash
curl -X POST "http://localhost:8000/set-webhook" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://yourdomain.com/webhook"}'
```

### Method 3: Using curl directly

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/webhook"}'
```

### Verify Webhook Status

Check if webhook is set correctly:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

## Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test Webhook Locally

Send a test webhook payload:
```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {
        "id": 123456,
        "is_bot": false,
        "first_name": "Test"
      },
      "chat": {
        "id": 123456,
        "type": "private"
      },
      "date": 1234567890,
      "text": "Hello, bot!"
    }
  }'
```

### 3. Test with Telegram

1. Find your bot on Telegram using its username
2. Send it a message
3. Check server logs to see the request processing

## Deployment

### Recommended Platforms

- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://heroku.com
- **DigitalOcean App Platform**: https://www.digitalocean.com/products/app-platform
- **AWS EC2/Lambda**
- **Google Cloud Run**

### Deployment Checklist

- [ ] Set environment variables on hosting platform
- [ ] Ensure server is accessible via HTTPS
- [ ] Set Telegram webhook to your deployment URL
- [ ] Test with a message on Telegram
- [ ] Monitor logs for errors

### Environment Variables for Deployment

Make sure to set these on your hosting platform:
```
TELEGRAM_BOT_TOKEN=<your_token>
LLM_PROVIDER=openai
LLM_API_KEY=<your_key>
LLM_MODEL=gpt-4o-mini
PORT=8000
```

## Switching LLM Providers

To switch between providers, simply update your `.env` file:

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
Health check and service info

### `GET /health`
Simple health check endpoint

### `POST /webhook`
Main webhook endpoint for Telegram updates

### `POST /set-webhook`
Helper endpoint to programmatically set Telegram webhook

**Request:**
```json
{
  "webhook_url": "https://yourdomain.com/webhook"
}
```

## Logging

Logs are output to stdout with the following format:
```
2024-01-15 10:30:45 - text-to-llm - INFO - Message received from chat 123456
```

View logs in real-time:
```bash
uvicorn app.main:app --reload | tee bot.log
```

## Troubleshooting

### Bot not responding

1. **Check webhook status:**
   ```
   https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```

2. **Verify environment variables:**
   ```bash
   python -c "from app.config import config; config.validate()"
   ```

3. **Check server logs** for error messages

4. **Test webhook endpoint** with curl

### LLM API Errors

- Verify your API key is valid
- Check API usage limits/quotas
- Ensure correct model name for provider
- Review server logs for detailed error messages

### Server won't start

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists and has correct values
- Check port 8000 is not already in use

## Contributing

To contribute:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Create a pull request and send me a message in the discord

## License

None

---

**Built with:**
- FastAPI
- Python 3.8+
- Telegram Bot API
- Compatibilty spanning OpenAI/Anthropic/xAI APIs
