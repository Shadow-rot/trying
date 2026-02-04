"""
Bot Client Module
Handles Pyrogram client initialization and management
"""
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from config import config
from core.logger import bot_logger
from core.database import db


class BotClient:
    """Main Bot Client"""
    
    def __init__(self):
        """Initialize bot client"""
        self.app = Client(
            name="advanced_bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="plugins") if config.ENABLE_PLUGINS else None,
            parse_mode=ParseMode.MARKDOWN,
            workdir="./sessions",
            max_concurrent_transmissions=config.MAX_WORKERS
        )
        
        self.started = False
    
    async def start(self):
        """Start the bot"""
        try:
            bot_logger.info("🚀 Starting bot...")
            
            # Validate configuration
            if not config.validate():
                bot_logger.critical("❌ Invalid configuration. Please check .env file")
                return False
            
            # Connect to database
            if config.ENABLE_DATABASE:
                await db.connect()
            
            # Start pyrogram client
            await self.app.start()
            
            # Get bot info
            me = await self.app.get_me()
            bot_logger.success(f"✅ Bot started as @{me.username}")
            bot_logger.info(f"📊 Bot ID: {me.id}")
            bot_logger.info(f"👤 Owner ID: {config.OWNER_ID}")
            bot_logger.info(f"🔧 Command Prefix: {config.COMMAND_PREFIX}")
            bot_logger.info(f"🔌 Plugins: {'Enabled' if config.ENABLE_PLUGINS else 'Disabled'}")
            
            self.started = True
            
            # Send startup message to owner
            if config.OWNER_ID:
                try:
                    await self.app.send_message(
                        config.OWNER_ID,
                        f"✅ **Bot Started Successfully!**\n\n"
                        f"🤖 **Username:** @{me.username}\n"
                        f"🆔 **Bot ID:** `{me.id}`\n"
                        f"📦 **Version:** `{config.BOT_VERSION}`\n"
                        f"🔧 **Prefix:** `{config.COMMAND_PREFIX}`\n\n"
                        f"Type `{config.COMMAND_PREFIX}help` to see available commands."
                    )
                except Exception as e:
                    bot_logger.warning(f"Could not send startup message: {e}")
            
            return True
            
        except Exception as e:
            bot_logger.critical(f"❌ Failed to start bot: {e}")
            return False
    
    async def stop(self):
        """Stop the bot"""
        try:
            bot_logger.info("🛑 Stopping bot...")
            
            # Send shutdown message to owner
            if config.OWNER_ID and self.started:
                try:
                    await self.app.send_message(
                        config.OWNER_ID,
                        "🛑 **Bot Stopped**"
                    )
                except Exception:
                    pass
            
            # Disconnect from database
            if config.ENABLE_DATABASE:
                await db.disconnect()
            
            # Stop pyrogram client
            await self.app.stop()
            
            bot_logger.success("✅ Bot stopped successfully")
            
        except Exception as e:
            bot_logger.error(f"❌ Error while stopping bot: {e}")
    
    async def restart(self):
        """Restart the bot"""
        bot_logger.info("🔄 Restarting bot...")
        await self.stop()
        await self.start()
    
    def run(self):
        """Run the bot (blocking)"""
        try:
            self.app.run(self.start())
            idle()
        except KeyboardInterrupt:
            bot_logger.info("🛑 Bot stopped by user (Ctrl+C)")
        except Exception as e:
            bot_logger.critical(f"❌ Fatal error: {e}")
        finally:
            if self.started:
                self.app.run(self.stop())


# Create bot client instance
bot = BotClient()
