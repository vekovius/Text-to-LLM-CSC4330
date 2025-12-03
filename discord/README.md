```markdown
# Discord Bot for Text-to-LLM-CSC4330

This folder contains a small Discord bot that forwards prompts to a LLM backend (local HTTP endpoint) or OpenAI.

Quickstart
1. Copy .env.example to .env and set your values.
2. Create a Python venv and install dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
3. Run:
   python bot.py

Environment variables
- DISCORD_TOKEN (required)
- LLM_SERVER_URL (optional) — e.g. http://host:port/llm, expects JSON {"reply": "..."} or {"output": "..."}
- OPENAI_API_KEY (optional)
- OPENAI_MODEL (optional, default gpt-3.5-turbo)

Bot behavior
- !ask <question> — ask LLM
- Mention bot in a channel with a prompt — bot replies
- Send DM to bot — bot replies

Notes
- Do not commit real tokens to the repository.
- If you run a local LLM, ensure the HTTP endpoint accepts POST JSON {"prompt": "..."} and returns JSON with a "reply" or "output" field.
```
