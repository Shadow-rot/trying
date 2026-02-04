"""
Advanced Telegram Bot
Main entry point for the bot application
"""
import os
import sys
from core.client import bot
from core.logger import bot_logger
from config import config


def main():
    """Main function to start the bot"""
    
    # Print banner
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     Advanced Telegram Bot                ║
    ║     Version: 2.0.0                       ║
    ║     Framework: Pyrogram                  ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    bot_logger.info("=" * 50)
    bot_logger.info("Starting Advanced Telegram Bot")
    bot_logger.info("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        bot_logger.critical("❌ .env file not found!")
        bot_logger.info("Please copy .env.example to .env and fill in your credentials")
        sys.exit(1)
    
    # Validate configuration
    if not config.validate():
        bot_logger.critical("❌ Configuration validation failed!")
        bot_logger.info("Please check your .env file")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    
    # Run the bot
    try:
        bot_logger.info("🚀 Initializing bot...")
        bot.run()
    except KeyboardInterrupt:
        bot_logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        bot_logger.critical(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
