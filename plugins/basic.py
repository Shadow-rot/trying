"""
Basic Commands Plugin
Essential bot commands like ping, alive, stats
"""
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from utils.decorators import log_errors
from utils.helpers import get_readable_time, get_system_stats, get_uptime
from core.database import db

# Bot start time
START_TIME = time.time()


@Client.on_message(filters.command("ping", prefixes=config.COMMAND_PREFIX))
@log_errors
async def ping_command(client: Client, message: Message):
    """Check bot response time"""
    start = time.time()
    msg = await message.reply_text("🏓 **Pinging...**")
    end = time.time()
    
    ping_time = (end - start) * 1000
    
    await msg.edit_text(
        f"🏓 **Pong!**\n"
        f"⚡ **Response Time:** `{ping_time:.2f}ms`\n"
        f"⏱️ **Uptime:** `{get_uptime(START_TIME)}`"
    )


@Client.on_message(filters.command("alive", prefixes=config.COMMAND_PREFIX))
@log_errors
async def alive_command(client: Client, message: Message):
    """Check if bot is alive"""
    me = await client.get_me()
    
    uptime = get_uptime(START_TIME)
    
    alive_text = (
        f"✅ **Bot is Alive!**\n\n"
        f"🤖 **Bot Name:** {me.first_name}\n"
        f"👤 **Username:** @{me.username}\n"
        f"🆔 **Bot ID:** `{me.id}`\n"
        f"📦 **Version:** `{config.BOT_VERSION}`\n"
        f"⏱️ **Uptime:** `{uptime}`\n"
        f"🔧 **Prefix:** `{config.COMMAND_PREFIX}`\n"
        f"🐍 **Python:** 3.10+\n"
        f"📚 **Framework:** Pyrogram"
    )
    
    await message.reply_text(alive_text)


@Client.on_message(filters.command("stats", prefixes=config.COMMAND_PREFIX))
@log_errors
async def stats_command(client: Client, message: Message):
    """Show bot statistics"""
    me = await client.get_me()
    system = get_system_stats()
    uptime = get_uptime(START_TIME)
    
    # Get user count from database
    users_count = 0
    if db.connected:
        users = await db.get_all_users()
        users_count = len(users)
    
    stats_text = (
        f"📊 **Bot Statistics**\n\n"
        f"**Bot Info:**\n"
        f"• Name: {me.first_name}\n"
        f"• Username: @{me.username}\n"
        f"• ID: `{me.id}`\n"
        f"• Uptime: `{uptime}`\n\n"
        f"**System Stats:**\n"
        f"• CPU: `{system['cpu']}%`\n"
        f"• RAM: `{system['memory_used']} / {system['memory_total']}` ({system['memory_percent']}%)\n"
        f"• Disk: `{system['disk_used']} / {system['disk_total']}` ({system['disk_percent']}%)\n\n"
        f"**Database:**\n"
        f"• Status: {'✅ Connected' if db.connected else '❌ Disconnected'}\n"
        f"• Users: `{users_count}`\n\n"
        f"**Configuration:**\n"
        f"• Plugins: {'✅ Enabled' if config.ENABLE_PLUGINS else '❌ Disabled'}\n"
        f"• Database: {'✅ Enabled' if config.ENABLE_DATABASE else '❌ Disabled'}\n"
        f"• Owner: `{config.OWNER_ID}`\n"
        f"• Sudo Users: `{len(config.SUDO_USERS)}`"
    )
    
    await message.reply_text(stats_text)


@Client.on_message(filters.command("info", prefixes=config.COMMAND_PREFIX))
@log_errors
async def info_command(client: Client, message: Message):
    """Get user/chat information"""
    # Check if replying to a message
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        target_message = message.reply_to_message
    else:
        user = message.from_user
        target_message = message
    
    # Get user info
    info_text = f"👤 **User Information**\n\n"
    info_text += f"**Name:** {user.first_name}"
    if user.last_name:
        info_text += f" {user.last_name}"
    info_text += f"\n**User ID:** `{user.id}`\n"
    
    if user.username:
        info_text += f"**Username:** @{user.username}\n"
    
    info_text += f"**Is Bot:** {'✅ Yes' if user.is_bot else '❌ No'}\n"
    
    if hasattr(user, 'is_premium'):
        info_text += f"**Premium:** {'✅ Yes' if user.is_premium else '❌ No'}\n"
    
    if hasattr(user, 'is_verified'):
        info_text += f"**Verified:** {'✅ Yes' if user.is_verified else '❌ No'}\n"
    
    # Add chat info if in group
    if message.chat.type != "private":
        info_text += f"\n💬 **Chat Information**\n\n"
        info_text += f"**Chat Title:** {message.chat.title}\n"
        info_text += f"**Chat ID:** `{message.chat.id}`\n"
        info_text += f"**Chat Type:** {message.chat.type}\n"
        
        if message.chat.username:
            info_text += f"**Username:** @{message.chat.username}\n"
    
    await message.reply_text(info_text)


@Client.on_message(filters.command("id", prefixes=config.COMMAND_PREFIX))
@log_errors
async def id_command(client: Client, message: Message):
    """Get user/chat ID"""
    id_text = f"🆔 **IDs**\n\n"
    id_text += f"**Your ID:** `{message.from_user.id}`\n"
    id_text += f"**Chat ID:** `{message.chat.id}`\n"
    
    if message.reply_to_message:
        id_text += f"**Replied User ID:** `{message.reply_to_message.from_user.id}`\n"
        if message.reply_to_message.forward_from:
            id_text += f"**Forwarded From ID:** `{message.reply_to_message.forward_from.id}`\n"
    
    await message.reply_text(id_text)
