"""
Twitter Controller - Handles Twitter/X bot interactions.
Supports:
 - Listening for incoming DMs
 - Replying to DMs
 - Handling mentions
"""

import asyncio
import tweepy
from app.llm_service import llm_service
from app.config import config
from app.utils.logger import logger


class TwitterController:

    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_SECRET,
            bearer_token=config.TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=True
        )

    async def send_dm(self, user_id: str, text: str):
        """Send a DM."""
        try:
            self.client.send_direct_message(event={
                "type": "message_create",
                "message_create": {
                    "target": {"recipient_id": user_id},
                    "message_data": {"text": text}
                }
            })
            logger.info(f"Sent DM to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send DM: {e}")

    async def process_incoming_dm(self, dm):
        """Generate LLM reply to an incoming DM."""
        sender_id = dm.message_create["sender_id"]
        text = dm.message_create["message_data"]["text"]

        logger.info(f"DM received from {sender_id}: {text}")

        reply = await llm_service.generate(text)
        await self.send_dm(sender_id, reply)

    async def start_dm_listener(self):
        """
        Continuously polls Twitter for new DMs.
        (Twitter does not support webhooks for DMs unless enterprise)
        """
        logger.info("Twitter DM listener started...")
        last_id = None

        while True:
            try:
                dms = self.client.get_direct_messages()
                events = dms["events"]

                for dm in events:
                    dm_id = dm["id"]

                    if dm_id != last_id:
                        await self.process_incoming_dm(dm)
                        last_id = dm_id

            except Exception as e:
                logger.error(f"DM listener error: {e}")

            await asyncio.sleep(3)  # Poll every 3 seconds


twitter_controller = TwitterController()
