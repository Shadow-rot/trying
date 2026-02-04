"""
Decorators Module
Custom decorators for access control and error handling
"""
from functools import wraps
from pyrogram import Client
from pyrogram.types import Message
from config import config
from core.logger import bot_logger


def owner_only(func):
    """Decorator to restrict command to bot owner only"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if not config.is_owner(message.from_user.id):
            await message.reply_text("❌ This command is only available to the bot owner.")
            return
        return await func(client, message)
    return wrapper


def sudo_only(func):
    """Decorator to restrict command to sudo users"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if not config.is_sudo(message.from_user.id):
            await message.reply_text("❌ You don't have permission to use this command.")
            return
        return await func(client, message)
    return wrapper


def log_errors(func):
    """Decorator to log errors and send user-friendly messages"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        try:
            return await func(client, message)
        except Exception as e:
            bot_logger.error(f"Error in {func.__name__}: {e}")
            await message.reply_text(
                f"❌ **An error occurred:**\n`{str(e)}`\n\n"
                f"This error has been logged."
            )
    return wrapper


def rate_limit(seconds: int = 5):
    """Decorator to rate limit command usage"""
    user_last_used = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            user_id = message.from_user.id
            import time
            current_time = time.time()
            
            if user_id in user_last_used:
                time_passed = current_time - user_last_used[user_id]
                if time_passed < seconds:
                    remaining = int(seconds - time_passed)
                    await message.reply_text(
                        f"⏳ Please wait {remaining} seconds before using this command again."
                    )
                    return
            
            user_last_used[user_id] = current_time
            return await func(client, message)
        return wrapper
    return decorator


def group_only(func):
    """Decorator to restrict command to groups only"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.chat.type == "private":
            await message.reply_text("❌ This command can only be used in groups.")
            return
        return await func(client, message)
    return wrapper


def admin_only(func):
    """Decorator to restrict command to group admins"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.chat.type == "private":
            await message.reply_text("❌ This command can only be used in groups.")
            return
        
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Owner and sudo users bypass admin check
        if config.is_sudo(user_id):
            return await func(client, message)
        
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in ["creator", "administrator"]:
                await message.reply_text("❌ This command is only available to group administrators.")
                return
        except Exception as e:
            bot_logger.error(f"Error checking admin status: {e}")
            await message.reply_text("❌ Could not verify admin status.")
            return
        
        return await func(client, message)
    return wrapper
