"""
Help Plugin
Display available commands and usage information
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from utils.decorators import log_errors

HELP_TEXT = f"""
🤖 **Advanced Telegram Bot - Commands**

**📌 Basic Commands**
• `{config.COMMAND_PREFIX}help` - Show this help message
• `{config.COMMAND_PREFIX}alive` - Check if bot is alive
• `{config.COMMAND_PREFIX}ping` - Check bot response time
• `{config.COMMAND_PREFIX}start` - Start the bot
• `{config.COMMAND_PREFIX}stats` - Show bot statistics

**🔧 Utility Commands**
• `{config.COMMAND_PREFIX}calc <expression>` - Calculate math expression
• `{config.COMMAND_PREFIX}weather <city>` - Get weather information
• `{config.COMMAND_PREFIX}translate <text>` - Translate text to English
• `{config.COMMAND_PREFIX}info` - Get user/chat information
• `{config.COMMAND_PREFIX}id` - Get user/chat ID

**📥 Media Commands**
• `{config.COMMAND_PREFIX}download <url>` - Download media from URL
• `{config.COMMAND_PREFIX}yt <url>` - Download YouTube video
• `{config.COMMAND_PREFIX}ytaudio <url>` - Download YouTube audio

**👥 Group Admin Commands** (Requires Admin)
• `{config.COMMAND_PREFIX}ban <reply/username>` - Ban a user
• `{config.COMMAND_PREFIX}unban <reply/username>` - Unban a user
• `{config.COMMAND_PREFIX}mute <reply/username>` - Mute a user
• `{config.COMMAND_PREFIX}unmute <reply/username>` - Unmute a user
• `{config.COMMAND_PREFIX}kick <reply/username>` - Kick a user
• `{config.COMMAND_PREFIX}promote <reply/username>` - Promote to admin
• `{config.COMMAND_PREFIX}demote <reply/username>` - Demote admin
• `{config.COMMAND_PREFIX}pin <reply>` - Pin a message
• `{config.COMMAND_PREFIX}unpin <reply>` - Unpin a message

**👤 Owner Commands** (Owner Only)
• `{config.COMMAND_PREFIX}restart` - Restart the bot
• `{config.COMMAND_PREFIX}broadcast <message>` - Broadcast to all users
• `{config.COMMAND_PREFIX}shell <command>` - Execute shell command
• `{config.COMMAND_PREFIX}logs` - Get bot logs

**ℹ️ Info**
• **Bot Version:** {config.BOT_VERSION}
• **Command Prefix:** `{config.COMMAND_PREFIX}`
• **Owner:** `{config.OWNER_ID}`

**📚 Support:** Report issues to bot owner
"""


@Client.on_message(filters.command(["help", "start"], prefixes=config.COMMAND_PREFIX) & filters.private)
@log_errors
async def help_command(client: Client, message: Message):
    """Display help message"""
    await message.reply_text(
        HELP_TEXT,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("start", prefixes="/") & filters.private)
@log_errors
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    me = await client.get_me()
    await message.reply_text(
        f"👋 **Hello {message.from_user.first_name}!**\n\n"
        f"I'm {me.first_name}, an advanced Telegram bot.\n\n"
        f"Use `{config.COMMAND_PREFIX}help` to see all available commands.\n\n"
        f"**Quick Start:**\n"
        f"• `{config.COMMAND_PREFIX}ping` - Test bot response\n"
        f"• `{config.COMMAND_PREFIX}alive` - Check bot status\n"
        f"• `{config.COMMAND_PREFIX}help` - Full command list"
    )


@Client.on_message(filters.command("commands", prefixes=config.COMMAND_PREFIX))
@log_errors
async def commands_list(client: Client, message: Message):
    """List all available commands"""
    await message.reply_text(HELP_TEXT, disable_web_page_preview=True)
