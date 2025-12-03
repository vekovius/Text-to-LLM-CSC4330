"""
Data models for Telegram messages and LLM interactions.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TelegramUser(BaseModel):
    """Represents a Telegram user."""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    """Represents a Telegram chat."""
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    """Represents a Telegram message."""
    message_id: int
    from_: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None


class TelegramUpdate(BaseModel):
    """
    Represents a Telegram webhook update.
    This is the main payload received from Telegram.
    """
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None


class LLMRequest(BaseModel):
    """Represents a request to the LLM service."""
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class LLMResponse(BaseModel):
    """Represents a response from the LLM service."""
    text: str
    model: str
    provider: str
    tokens_used: Optional[int] = None


class TelegramSendMessageRequest(BaseModel):
    """Request model for sending a Telegram message."""
    chat_id: int
    text: str
    parse_mode: Optional[str] = None
    reply_to_message_id: Optional[int] = None
