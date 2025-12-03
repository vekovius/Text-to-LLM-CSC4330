"""
Configuration management for the Text-to-LLM Telegram Bot.
Loads environment variables using python-dotenv.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_API_BASE_URL: str = "https://api.telegram.org"
    
    # Whatsapp Bot Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # Options: openai, anthropic, xai
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default model for OpenAI

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Optional: Max tokens for LLM response
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))

    @classmethod
    def validate(cls) -> None:
        """
        Validates that all required configuration values are present.
        Raises ValueError if any required config is missing.
        """
        errors = []

        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")

        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is required")

        if cls.LLM_PROVIDER not in ["openai", "anthropic", "xai"]:
            errors.append(f"LLM_PROVIDER must be one of: openai, anthropic, xai (got: {cls.LLM_PROVIDER})")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors))

    @classmethod
    def get_telegram_url(cls, method: str) -> str:
        """
        Constructs Telegram API URL for a given method.

        Args:
            method: The Telegram Bot API method name (e.g., 'sendMessage')

        Returns:
            Full URL for the Telegram API endpoint
        """
        return f"{cls.TELEGRAM_API_BASE_URL}/bot{cls.TELEGRAM_BOT_TOKEN}/{method}"


# Create a singleton instance
config = Config()
"""
Configuration management for the Text-to-LLM Telegram Bot.
Loads environment variables using python-dotenv.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_API_BASE_URL: str = "https://api.telegram.org"

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # Options: openai, anthropic, xai
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default model for OpenAI

    X_API_KEY = os.getenv("X_API_KEY")
    X_API_SECRET = os.getenv("X_API_SECRET")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Optional: Max tokens for LLM response
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))

    @classmethod
    def validate(cls) -> None:
        """
        Validates that all required configuration values are present.
        Raises ValueError if any required config is missing.
        """
        errors = []

        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")

        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is required")

        if cls.LLM_PROVIDER not in ["openai", "anthropic", "xai"]:
            errors.append(f"LLM_PROVIDER must be one of: openai, anthropic, xai (got: {cls.LLM_PROVIDER})")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors))

    @classmethod
    def get_telegram_url(cls, method: str) -> str:
        """
        Constructs Telegram API URL for a given method.

        Args:
            method: The Telegram Bot API method name (e.g., 'sendMessage')

        Returns:
            Full URL for the Telegram API endpoint
        """
        return f"{cls.TELEGRAM_API_BASE_URL}/bot{cls.TELEGRAM_BOT_TOKEN}/{method}"


# Create a singleton instance
config = Config()
