"""
Usul Al-Din Educational Telegram Bot
Main Entry Point

Compatible with Render Free Tier Deployment
"""

import asyncio
import logging
from config import TELEGRAM_TOKEN, PORT
from app.bot import create_bot_application
from app.web import app

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def run_bot():
    """Run the Telegram bot with webhook"""
    application = create_bot_application()
    
    # Set webhook
    webhook_url = f"https://your-app-name.onrender.com/webhook"
    
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")
    
    # Start the application
    await application.start()
    logger.info("Bot started successfully!")
    
    # Keep the application running
    await application.updater.start_polling()


def run_web():
    """Run the Flask web server"""
    app.run(host='0.0.0.0', port=PORT, debug=False)


def main():
    """Main entry point"""
    import threading
    
    # Run bot in a separate thread (for polling mode)
    bot_thread = threading.Thread(target=lambda: asyncio.run(run_bot()), daemon=True)
    bot_thread.start()
    
    # Run web server
    logger.info(f"Starting web server on port {PORT}...")
    run_web()


if __name__ == "__main__":
    main()
