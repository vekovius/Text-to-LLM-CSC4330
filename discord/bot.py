cat > discord/bot.py <<'EOF'
#!/usr/bin/env python3
"""
Discord bot that forwards prompts to a local LLM HTTP endpoint or OpenAI and replies.
Place this file in discord/ and run with the environment variables defined in .env.
"""
import os
import asyncio
import logging
from typing import Optional

import httpx
from discord.ext import commands
import discord

# Optional: if you want to use the OpenAI python client directly, install it and uncomment:
# import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-llm-bot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN must be set in the environment")

LLM_SERVER_URL = os.getenv("LLM_SERVER_URL")  # e.g. http://localhost:8000/llm -> expects JSON response {"reply": "..."} or {"output": "..."}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # optional
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


class LLMClient:
    def __init__(self, server_url: Optional[str], openai_key: Optional[str]):
        self.server_url = server_url
        self.openai_key = openai_key
        # If using openai library, set API key here:
        # if self.openai_key:
        #     openai.api_key = self.openai_key

    async def ask(self, prompt: str) -> str:
        if self.server_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(self.server_url, json={"prompt": prompt})
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get("reply") or data.get("output") or str(data)
            except Exception as e:
                logger.exception("LLM server request failed")
                return f"LLM server error: {e}"

        # Optional: call OpenAI REST API directly if you prefer not to depend on openai lib
        if self.openai_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": DEFAULT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 512,
                }
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.exception("OpenAI request failed")
                return f"OpenAI error: {e}"

        return "No LLM backend configured. Set LLM_SERVER_URL or OPENAI_API_KEY."


llm_client = LLMClient(LLM_SERVER_URL, OPENAI_API_KEY)


@bot.event
async def on_ready():
    logger.info(f"Bot ready: {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    # Ignore bots (including self)
    if message.author.bot:
        return

    await bot.process_commands(message)

    content = message.content.strip()
    invoked = False
    prompt = None

    # If DM -> treat as query
    if isinstance(message.channel, discord.DMChannel):
        prompt = content
        invoked = True
    # If bot is mentioned -> use rest of message
    elif bot.user in message.mentions:
        # remove mention tokens
        mention_str = f"<@!{bot.user.id}>"
        prompt = content.replace(mention_str, "").strip()
        invoked = True

    if invoked and prompt:
        logger.info(f"Prompt from {message.author}: {prompt[:120]}")
        try:
            async with message.channel.typing():
                reply = await llm_client.ask(prompt)
                if not reply:
                    reply = "(no reply)"
                if len(reply) > 1900:
                    reply = reply[:1900] + "\n\n...[truncated]"
                await message.reply(reply, mention_author=False)
        except Exception as e:
            logger.exception("Failed to generate reply")
            await message.reply(f"Error generating reply: {e}", mention_author=False)


@bot.command(name="ask", help="Ask the LLM a question. Usage: !ask <your question>")
async def ask_cmd(ctx: commands.Context, *, query: str):
    await ctx.message.add_reaction("🤖")
    try:
        async with ctx.typing():
            reply = await llm_client.ask(query)
            if len(reply) > 1900:
                reply = reply[:1900] + "\n\n...[truncated]"
            await ctx.send(reply)
    except Exception as e:
        logger.exception("ask_cmd failed")
        await ctx.send(f"Error: {e}")


@bot.command(name="health", help="Check bot status")
async def health_cmd(ctx: commands.Context):
    await ctx.send("Bot is running.")


def main():
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
EOF
