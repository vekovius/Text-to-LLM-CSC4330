"""
Telegram Controller - Handles Telegram Bot API interactions.
Parses webhook payloads and sends messages back to users.
"""
import httpx
from typing import Optional, Dict, Any
from app.config import config
from app.models.message import TelegramUpdate, TelegramMessage
from app.utils.logger import logger


class TelegramController:
    """
    Controller for Telegram Bot API operations.
    Handles webhook parsing and message sending.
    """

    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.api_base = config.TELEGRAM_API_BASE_URL

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[TelegramUpdate]:
        """
        Parse incoming webhook payload from Telegram.

        Args:
            payload: Raw JSON payload from Telegram webhook

        Returns:
            Parsed TelegramUpdate object or None if parsing fails
        """
        try:
            update = TelegramUpdate(**payload)
            logger.info(f"Parsed webhook update: {update.update_id}")
            return update
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {str(e)}")
            return None

    def extract_message_data(self, update: TelegramUpdate) -> Optional[tuple[int, str]]:
        """
        Extract chat_id and message text from a Telegram update.

        Args:
            update: Parsed TelegramUpdate object

        Returns:
            Tuple of (chat_id, text) or None if no valid message found
        """
        # Handle regular messages
        if update.message and update.message.text:
            chat_id = update.message.chat.id
            text = update.message.text
            logger.info(f"Extracted message from chat {chat_id}: {text[:50]}...")
            return chat_id, text

        # Handle edited messages
        if update.edited_message and update.edited_message.text:
            chat_id = update.edited_message.chat.id
            text = update.edited_message.text
            logger.info(f"Extracted edited message from chat {chat_id}: {text[:50]}...")
            return chat_id, text

        logger.warning("No text message found in update")
        return None

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> bool:
        """
        Send a message to a Telegram chat using the Bot API.

        Args:
            chat_id: Target chat ID
            text: Message text to send
            parse_mode: Optional parse mode (e.g., "Markdown", "HTML")
            reply_to_message_id: Optional message ID to reply to

        Returns:
            True if message sent successfully, False otherwise

        API Docs: https://core.telegram.org/bots/api#sendmessage
        """
        url = config.get_telegram_url("sendMessage")

        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                if result.get("ok"):
                    logger.info(f"Message sent successfully to chat {chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API returned error: {result}")
                    return False

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error sending message: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
                return False

    async def send_typing_action(self, chat_id: int) -> bool:
        """
        Send 'typing' action to show the bot is processing.

        Args:
            chat_id: Target chat ID

        Returns:
            True if action sent successfully, False otherwise
        """
        url = config.get_telegram_url("sendChatAction")
        payload = {
            "chat_id": chat_id,
            "action": "typing"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.debug(f"Typing action sent to chat {chat_id}")
                return True
            except Exception as e:
                logger.warning(f"Failed to send typing action: {str(e)}")
                return False

    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Set the webhook URL for the Telegram bot.

        Args:
            webhook_url: Full HTTPS URL where Telegram will send updates

        Returns:
            True if webhook set successfully, False otherwise

        Note: This is a helper method. You can also set webhook via:
        https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>
        """
        url = config.get_telegram_url("setWebhook")
        payload = {
            "url": webhook_url
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()

                if result.get("ok"):
                    logger.info(f"Webhook set successfully to: {webhook_url}")
                    return True
                else:
                    logger.error(f"Failed to set webhook: {result}")
                    return False

            except Exception as e:
                logger.error(f"Error setting webhook: {str(e)}")
                return False


# Create singleton instance
telegram_controller = TelegramController()
