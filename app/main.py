"""
FastAPI Server - Main application entry point.
Handles Telegram webhook and orchestrates LLM responses.

Architecture:
User → Telegram Bot → /webhook → LLM Service → Telegram Bot → User
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import config
from app.telegram_controller import telegram_controller
from app.llm_service import llm_service
from app.utils.logger import logger
from app.routers import whatsapp 

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Validates configuration on startup.
    """
    # Startup
    logger.info("Starting Text-to-LLM Telegram Bot Server...")
    try:
        config.validate()
        logger.info(f"Configuration validated successfully")
        logger.info(f"LLM Provider: {config.LLM_PROVIDER}")
        logger.info(f"LLM Model: {config.LLM_MODEL}")
        logger.info("Server ready to accept webhook requests")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down server...")


# Initialize FastAPI app
app = FastAPI(
    title="Text-to-LLM Telegram Bot",
    description="A Telegram bot that forwards user messages to LLM providers (OpenAI, Anthropic, xAI)",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(whatsapp.router)

@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "status": "running",
        "service": "Text-to-LLM Telegram Bot",
        "provider": config.LLM_PROVIDER,
        "model": config.LLM_MODEL
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(request: Request):
    """
    Main webhook endpoint for receiving Telegram updates.

    Flow:
    1. Receive webhook payload from Telegram
    2. Parse and extract message data
    3. Send typing indicator to user
    4. Generate LLM response
    5. Send response back to user via Telegram

    Returns:
        JSON response with status
    """
    try:
        # Parse incoming webhook payload
        payload = await request.json()
        logger.info(f"Received webhook: {payload.get('update_id', 'unknown')}")

        # Parse Telegram update
        update = telegram_controller.parse_webhook(payload)
        if not update:
            logger.warning("Failed to parse webhook update")
            return JSONResponse({"status": "error", "message": "Invalid payload"}, status_code=400)

        # Extract message data
        message_data = telegram_controller.extract_message_data(update)
        if not message_data:
            logger.info("No actionable message in update")
            return JSONResponse({"status": "ok", "message": "No text message"})

        chat_id, user_text = message_data

        # Send typing indicator
        await telegram_controller.send_typing_action(chat_id)

        # Generate LLM response
        logger.info(f"Processing message: '{user_text[:100]}...'")
        try:
            llm_response = await llm_service.generate(user_text)
            logger.info(f"LLM response generated: {len(llm_response)} characters")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            error_message = "Sorry, I encountered an error processing your request. Please try again later."
            await telegram_controller.send_message(chat_id, error_message)
            return JSONResponse({"status": "error", "message": "LLM generation failed"}, status_code=500)

        # Send response back to user
        success = await telegram_controller.send_message(
            chat_id=chat_id,
            text=llm_response,
            reply_to_message_id=update.message.message_id if update.message else None
        )

        if success:
            logger.info(f"Response sent successfully to chat {chat_id}")
            return JSONResponse({"status": "ok"})
        else:
            logger.error(f"Failed to send response to chat {chat_id}")
            return JSONResponse({"status": "error", "message": "Failed to send message"}, status_code=500)

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/set-webhook")
async def set_webhook_endpoint(request: Request):
    """
    Helper endpoint to set Telegram webhook programmatically.

    Request body:
    {
        "webhook_url": "https://yourdomain.com/webhook"
    }

    Returns:
        Success/failure status
    """
    try:
        data = await request.json()
        webhook_url = data.get("webhook_url")

        if not webhook_url:
            raise HTTPException(status_code=400, detail="webhook_url is required")

        success = await telegram_controller.set_webhook(webhook_url)

        if success:
            return {"status": "ok", "message": f"Webhook set to: {webhook_url}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set-webhook endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Entry point for running with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
"""
FastAPI Server - Main application entry point.
Handles Telegram webhook and orchestrates LLM responses.

Architecture:
User → Telegram Bot → /webhook → LLM Service → Telegram Bot → User
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import config
from app.telegram_controller import telegram_controller
from app.llm_service import llm_service
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Validates configuration on startup.
    """
    # Startup
    logger.info("Starting Text-to-LLM Telegram Bot Server...")
    try:
        config.validate()
        logger.info(f"Configuration validated successfully")
        logger.info(f"LLM Provider: {config.LLM_PROVIDER}")
        logger.info(f"LLM Model: {config.LLM_MODEL}")
        logger.info("Server ready to accept webhook requests")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down server...")


# Initialize FastAPI app
app = FastAPI(
    title="Text-to-LLM Telegram Bot",
    description="A Telegram bot that forwards user messages to LLM providers (OpenAI, Anthropic, xAI)",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "status": "running",
        "service": "Text-to-LLM Telegram Bot",
        "provider": config.LLM_PROVIDER,
        "model": config.LLM_MODEL
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(request: Request):
    """
    Main webhook endpoint for receiving Telegram updates.

    Flow:
    1. Receive webhook payload from Telegram
    2. Parse and extract message data
    3. Send typing indicator to user
    4. Generate LLM response
    5. Send response back to user via Telegram

    Returns:
        JSON response with status
    """
    try:
        # Parse incoming webhook payload
        payload = await request.json()
        logger.info(f"Received webhook: {payload.get('update_id', 'unknown')}")

        # Parse Telegram update
        update = telegram_controller.parse_webhook(payload)
        if not update:
            logger.warning("Failed to parse webhook update")
            return JSONResponse({"status": "error", "message": "Invalid payload"}, status_code=400)

        # Extract message data
        message_data = telegram_controller.extract_message_data(update)
        if not message_data:
            logger.info("No actionable message in update")
            return JSONResponse({"status": "ok", "message": "No text message"})

        chat_id, user_text = message_data

        # Send typing indicator
        await telegram_controller.send_typing_action(chat_id)

        # Generate LLM response
        logger.info(f"Processing message: '{user_text[:100]}...'")
        try:
            llm_response = await llm_service.generate(user_text)
            logger.info(f"LLM response generated: {len(llm_response)} characters")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            error_message = "Sorry, I encountered an error processing your request. Please try again later."
            await telegram_controller.send_message(chat_id, error_message)
            return JSONResponse({"status": "error", "message": "LLM generation failed"}, status_code=500)

        # Send response back to user
        success = await telegram_controller.send_message(
            chat_id=chat_id,
            text=llm_response,
            reply_to_message_id=update.message.message_id if update.message else None
        )

        if success:
            logger.info(f"Response sent successfully to chat {chat_id}")
            return JSONResponse({"status": "ok"})
        else:
            logger.error(f"Failed to send response to chat {chat_id}")
            return JSONResponse({"status": "error", "message": "Failed to send message"}, status_code=500)

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/set-webhook")
async def set_webhook_endpoint(request: Request):
    """
    Helper endpoint to set Telegram webhook programmatically.

    Request body:
    {
        "webhook_url": "https://yourdomain.com/webhook"
    }

    Returns:
        Success/failure status
    """
    try:
        data = await request.json()
        webhook_url = data.get("webhook_url")

        if not webhook_url:
            raise HTTPException(status_code=400, detail="webhook_url is required")

        success = await telegram_controller.set_webhook(webhook_url)

        if success:
            return {"status": "ok", "message": f"Webhook set to: {webhook_url}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set-webhook endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Entry point for running with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
