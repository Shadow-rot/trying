"""
Admin Commands Plugin
Comprehensive group administration commands with moderation features
Author: Enhanced Version
Features: Ban, Mute, Kick, Warn, Promote, Lock, Purge, and more
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, ChatPrivileges
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, RPCError, FloodWait
from datetime import datetime, timedelta
import asyncio
from typing import Optional, Dict
from config import config
from utils.decorators import log_errors, admin_only, group_only
from core.logger import bot_logger

# Try to import extract_args, provide fallback if it fails
try:
    from utils.helpers import extract_args
except:
    def extract_args(message: Message) -> str:
        """Fallback extract_args function"""
        if not message.text:
            return ""
        parts = message.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""

# In-memory storage for warnings (consider using database for production)
user_warnings: Dict[int, Dict[int, int]] = {}  # {chat_id: {user_id: warning_count}}
MAX_WARNINGS = 3


def safe_extract_args(message: Message) -> str:
    """Safely extract arguments from message"""
    try:
        args = safe_extract_args(message)
        if args and isinstance(args, str):
            return args
        return ""
    except Exception:
        # Fallback: manual extraction
        if not message.text:
            return ""
        parts = message.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""


async def get_user_from_message(client: Client, message: Message):
    """Extract user from replied message or username/ID"""
    if message.reply_to_message:
        return message.reply_to_message.from_user

    args = safe_extract_args(message)
    if not args:
        await message.reply_text("❌ Reply to a user or provide username/ID")
        return None

    try:
        # Try to parse as user ID (numbers only)
        if args.strip().isdigit():
            user = await client.get_users(int(args.strip()))
            return user
        
        # Try username (with or without @)
        username = args.strip().lstrip('@')
        user = await client.get_users(username)
        return user
    except Exception as e:
        await message.reply_text(
            f"❌ Could not find user\n"
            f"💡 **Tip:** Reply to the user's message instead of using username"
        )
        return None


def parse_time(time_str: str) -> Optional[int]:
    """Parse time string to seconds (e.g., '5m', '2h', '1d')"""
    if not time_str:
        return None
    
    time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    
    try:
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        
        if unit in time_units:
            return value * time_units[unit]
    except (ValueError, IndexError):
        pass
    
    return None


# ==================== BAN COMMANDS ====================

@Client.on_message(filters.command("ban", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def ban_user(client: Client, message: Message):
    """Ban a user from the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    # Get reason if provided
    args = safe_extract_args(message)
    reason = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "No reason provided"

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.reply_text(
            f"🚫 **User Banned**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to ban users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot ban administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("unban", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def unban_user(client: Client, message: Message):
    """Unban a user from the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    try:
        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply_text(
            f"✅ **User Unbanned**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unban users")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("tban", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def temp_ban_user(client: Client, message: Message):
    """Temporarily ban a user (Usage: /tban <user> <time>)"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    args = safe_extract_args(message)
    time_str = args.split()[1] if args and len(args.split()) > 1 else None
    
    if not time_str:
        await message.reply_text("❌ Usage: `/tban <user> <time>` (e.g., 5m, 2h, 1d)")
        return

    duration = parse_time(time_str)
    if not duration:
        await message.reply_text("❌ Invalid time format. Use: 5m, 2h, 1d, etc.")
        return

    try:
        until_date = datetime.now() + timedelta(seconds=duration)
        await client.ban_chat_member(message.chat.id, user.id, until_date=until_date)
        await message.reply_text(
            f"⏰ **User Temporarily Banned**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"⏱️ Duration: {time_str}\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to ban users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot ban administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== KICK COMMANDS ====================

@Client.on_message(filters.command("kick", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def kick_user(client: Client, message: Message):
    """Kick a user from the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    args = safe_extract_args(message)
    reason = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "No reason provided"

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply_text(
            f"👢 **User Kicked**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to kick users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot kick administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== MUTE COMMANDS ====================

@Client.on_message(filters.command("mute", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def mute_user(client: Client, message: Message):
    """Mute a user in the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    args = safe_extract_args(message)
    reason = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "No reason provided"

    try:
        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions()
        )
        await message.reply_text(
            f"🔇 **User Muted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to mute users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot mute administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("unmute", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def unmute_user(client: Client, message: Message):
    """Unmute a user in the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    try:
        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        await message.reply_text(
            f"🔊 **User Unmuted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unmute users")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("tmute", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def temp_mute_user(client: Client, message: Message):
    """Temporarily mute a user (Usage: /tmute <user> <time>)"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    args = safe_extract_args(message)
    time_str = args.split()[1] if args and len(args.split()) > 1 else None
    
    if not time_str:
        await message.reply_text("❌ Usage: `/tmute <user> <time>` (e.g., 5m, 2h, 1d)")
        return

    duration = parse_time(time_str)
    if not duration:
        await message.reply_text("❌ Invalid time format. Use: 5m, 2h, 1d, etc.")
        return

    try:
        until_date = datetime.now() + timedelta(seconds=duration)
        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions(),
            until_date=until_date
        )
        await message.reply_text(
            f"⏰ **User Temporarily Muted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"⏱️ Duration: {time_str}\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to mute users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot mute administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== PROMOTE/DEMOTE COMMANDS ====================

@Client.on_message(filters.command("promote", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def promote_user(client: Client, message: Message):
    """Promote a user to admin"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    # Get custom title if provided
    args = safe_extract_args(message)
    title = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "Admin"
    title = title[:16]  # Telegram limit

    try:
        # Get chat type to determine available privileges
        chat = await client.get_chat(message.chat.id)
        is_channel = chat.type == "channel"
        
        # Set privileges based on chat type
        if is_channel:
            privileges = ChatPrivileges(
                can_manage_chat=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_manage_video_chats=False,  # Not available in channels
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        else:
            # For groups and supergroups
            privileges = ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,  # Don't give promote rights by default
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=privileges
        )
        
        # Set custom title (this might fail silently in some cases)
        try:
            await client.set_administrator_title(message.chat.id, user.id, title)
        except:
            pass

        await message.reply_text(
            f"⬆️ **User Promoted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"🏷️ Title: {title}\n"
            f"✅ Now has admin privileges\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text(
            "❌ I need admin rights to promote users\n"
            "💡 Make sure I have 'Add Admins' permission"
        )
    except UserAdminInvalid:
        await message.reply_text("❌ This user is already an admin")
    except RPCError as e:
        error_msg = str(e)
        if "RIGHT_FORBIDDEN" in error_msg or "403" in error_msg:
            await message.reply_text(
                "❌ **Cannot promote user**\n\n"
                "**Possible reasons:**\n"
                "• Bot doesn't have 'Add Admins' permission\n"
                "• Bot cannot give rights it doesn't have\n"
                "• User may already be admin with higher rights\n\n"
                "💡 **Solution:** Give bot 'Add Admins' permission in chat settings"
            )
        else:
            await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("fullpromote", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def full_promote_user(client: Client, message: Message):
    """Promote a user to admin with all rights (including add admins)"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    # Get custom title if provided
    args = safe_extract_args(message)
    title = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "Admin"
    title = title[:16]  # Telegram limit

    try:
        # Get chat type to determine available privileges
        chat = await client.get_chat(message.chat.id)
        is_channel = chat.type == "channel"
        
        # Set full privileges based on chat type
        if is_channel:
            privileges = ChatPrivileges(
                can_manage_chat=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_manage_video_chats=False,
                can_restrict_members=True,
                can_promote_members=True,  # Full rights
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        else:
            # For groups and supergroups
            privileges = ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,  # Full rights
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=privileges
        )
        
        # Set custom title
        try:
            await client.set_administrator_title(message.chat.id, user.id, title)
        except:
            pass

        await message.reply_text(
            f"⬆️ **User Fully Promoted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"🏷️ Title: {title}\n"
            f"✅ Now has **full** admin privileges (including add admins)\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text(
            "❌ I need admin rights to promote users\n"
            "💡 Make sure I have 'Add Admins' permission"
        )
    except UserAdminInvalid:
        await message.reply_text("❌ This user is already an admin")
    except RPCError as e:
        error_msg = str(e)
        if "RIGHT_FORBIDDEN" in error_msg or "403" in error_msg:
            await message.reply_text(
                "❌ **Cannot promote user**\n\n"
                "**Possible reasons:**\n"
                "• Bot doesn't have 'Add Admins' permission\n"
                "• Bot cannot give rights it doesn't have\n"
                "• User may already be admin with higher rights\n\n"
                "💡 **Solution:** Give bot 'Add Admins' permission in chat settings"
            )
        else:
            await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("demote", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def demote_user(client: Client, message: Message):
    """Demote an admin to regular user"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    try:
        # Properly demote by explicitly setting all privileges to False
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_post_messages=False,
                can_edit_messages=False
            )
        )
        await message.reply_text(
            f"⬇️ **User Demoted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"❌ Admin privileges removed\n"
            f"✅ User is now a regular member\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to demote users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot demote the group creator")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== WARNING SYSTEM ====================

@Client.on_message(filters.command("warn", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def warn_user(client: Client, message: Message):
    """Warn a user (3 warnings = auto ban)"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    chat_id = message.chat.id
    user_id = user.id

    # Initialize warnings dict for this chat if not exists
    if chat_id not in user_warnings:
        user_warnings[chat_id] = {}

    # Get reason
    args = safe_extract_args(message)
    reason = " ".join(args.split()[1:]) if args and len(args.split()) > 1 else "No reason provided"

    # Add warning
    current_warnings = user_warnings[chat_id].get(user_id, 0) + 1
    user_warnings[chat_id][user_id] = current_warnings

    if current_warnings >= MAX_WARNINGS:
        try:
            await client.ban_chat_member(chat_id, user_id)
            user_warnings[chat_id][user_id] = 0  # Reset warnings
            await message.reply_text(
                f"🚫 **User Auto-Banned**\n"
                f"👤 User: {user.mention}\n"
                f"🆔 ID: `{user_id}`\n"
                f"⚠️ Reached {MAX_WARNINGS} warnings\n"
                f"📝 Last reason: {reason}\n"
                f"👮 By: {message.from_user.mention}"
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to ban user: {e}")
    else:
        await message.reply_text(
            f"⚠️ **User Warned**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📊 Warnings: {current_warnings}/{MAX_WARNINGS}\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {message.from_user.mention}"
        )


@Client.on_message(filters.command("warnings", prefixes=config.COMMAND_PREFIX))
@group_only
@log_errors
async def check_warnings(client: Client, message: Message):
    """Check warnings for a user"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    chat_id = message.chat.id
    user_id = user.id
    warnings = user_warnings.get(chat_id, {}).get(user_id, 0)

    await message.reply_text(
        f"📊 **Warning Status**\n"
        f"👤 User: {user.mention}\n"
        f"🆔 ID: `{user_id}`\n"
        f"⚠️ Warnings: {warnings}/{MAX_WARNINGS}"
    )


@Client.on_message(filters.command("resetwarns", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def reset_warnings(client: Client, message: Message):
    """Reset warnings for a user"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    chat_id = message.chat.id
    user_id = user.id

    if chat_id in user_warnings and user_id in user_warnings[chat_id]:
        user_warnings[chat_id][user_id] = 0
        await message.reply_text(
            f"✅ **Warnings Reset**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user_id}`\n"
            f"👮 By: {message.from_user.mention}"
        )
    else:
        await message.reply_text("✅ User has no warnings")


# ==================== PIN COMMANDS ====================

@Client.on_message(filters.command("pin", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def pin_message(client: Client, message: Message):
    """Pin a message"""
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to pin it")
        return

    # Check if should notify
    args = safe_extract_args(message)
    notify = "silent" not in args.lower() if args else True

    try:
        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id,
            disable_notification=not notify
        )
        await message.reply_text("📌 **Message Pinned**")
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to pin messages")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("unpin", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def unpin_message(client: Client, message: Message):
    """Unpin a message"""
    try:
        if message.reply_to_message:
            await client.unpin_chat_message(
                message.chat.id,
                message.reply_to_message.id
            )
        else:
            await client.unpin_chat_message(message.chat.id)

        await message.reply_text("📍 **Message Unpinned**")
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unpin messages")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("unpinall", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def unpin_all_messages(client: Client, message: Message):
    """Unpin all messages in the chat"""
    try:
        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("📍 **All Messages Unpinned**")
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unpin messages")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== PURGE COMMANDS ====================

@Client.on_message(filters.command("purge", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def purge_messages(client: Client, message: Message):
    """Delete messages from replied message to current"""
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to purge from there")
        return

    try:
        message_ids = []
        start_id = message.reply_to_message.id
        end_id = message.id

        # Collect message IDs to delete
        for msg_id in range(start_id, end_id + 1):
            message_ids.append(msg_id)

        # Delete in chunks of 100 (Telegram limit)
        deleted_count = 0
        for i in range(0, len(message_ids), 100):
            chunk = message_ids[i:i + 100]
            try:
                await client.delete_messages(message.chat.id, chunk)
                deleted_count += len(chunk)
                await asyncio.sleep(1)  # Avoid flood limits
            except FloodWait as e:
                # FloodWait.x contains the wait time in Pyrogram 2.x
                wait_time = e.x if hasattr(e, 'x') else (e.value if hasattr(e, 'value') else 30)
                await asyncio.sleep(wait_time)
                await client.delete_messages(message.chat.id, chunk)
                deleted_count += len(chunk)

        status_msg = await message.reply_text(f"🗑️ **Purged {deleted_count} messages**")
        await asyncio.sleep(3)
        await status_msg.delete()

    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to delete messages")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("del", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def delete_message(client: Client, message: Message):
    """Delete the replied message"""
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to delete it")
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to delete messages")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== LOCK COMMANDS ====================

@Client.on_message(filters.command("lock", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def lock_chat(client: Client, message: Message):
    """Lock the chat (only admins can send messages)"""
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions()
        )
        await message.reply_text(
            f"🔒 **Chat Locked**\n"
            f"Only admins can send messages now\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to lock the chat")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("unlock", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def unlock_chat(client: Client, message: Message):
    """Unlock the chat (everyone can send messages)"""
    try:
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )
        await message.reply_text(
            f"🔓 **Chat Unlocked**\n"
            f"Everyone can send messages now\n"
            f"👮 By: {message.from_user.mention}"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unlock the chat")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== INFO COMMANDS ====================

@Client.on_message(filters.command("admins", prefixes=config.COMMAND_PREFIX))
@group_only
@log_errors
async def list_admins(client: Client, message: Message):
    """List all admins in the group"""
    try:
        admins = []
        
        # Try using ChatMembersFilter enum first
        try:
            from pyrogram.enums import ChatMembersFilter
            async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                status = "👑 Owner" if member.status == "creator" else "👮 Admin"
                custom_title = f" ({member.custom_title})" if member.custom_title else ""
                admins.append(f"{status} {member.user.mention}{custom_title}")
        except ImportError:
            # Fallback for older Pyrogram versions
            async for member in client.get_chat_members(message.chat.id, filter="administrators"):
                status = "👑 Owner" if member.status == "creator" else "👮 Admin"
                custom_title = f" ({member.custom_title})" if member.custom_title else ""
                admins.append(f"{status} {member.user.mention}{custom_title}")

        admin_list = "\n".join(admins)
        await message.reply_text(
            f"👥 **Group Administrators**\n\n{admin_list}\n\n"
            f"📊 Total: {len(admins)}"
        )
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("info", prefixes=config.COMMAND_PREFIX))
@group_only
@log_errors
async def user_info(client: Client, message: Message):
    """Get information about a user"""
    user = await get_user_from_message(client, message)
    if not user:
        return

    try:
        member = await client.get_chat_member(message.chat.id, user.id)
        
        status_emoji = {
            "creator": "👑",
            "administrator": "👮",
            "member": "👤",
            "restricted": "🚫",
            "left": "🚶",
            "kicked": "⛔"
        }
        
        status = status_emoji.get(member.status, "❓") + " " + member.status.title()
        
        info_text = (
            f"📋 **User Information**\n\n"
            f"👤 Name: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username}" if user.username else ""
        )
        
        if user.username:
            info_text += f"\n📱 Username: @{user.username}"
        
        info_text += f"\n📊 Status: {status}"
        
        if member.custom_title:
            info_text += f"\n🏷️ Title: {member.custom_title}"
        
        # Get warnings if any
        warnings = user_warnings.get(message.chat.id, {}).get(user.id, 0)
        if warnings > 0:
            info_text += f"\n⚠️ Warnings: {warnings}/{MAX_WARNINGS}"

        await message.reply_text(info_text)
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("chatinfo", prefixes=config.COMMAND_PREFIX))
@group_only
@log_errors
async def chat_info(client: Client, message: Message):
    """Get information about the current chat"""
    try:
        chat = await client.get_chat(message.chat.id)
        member_count = await client.get_chat_members_count(message.chat.id)
        
        info_text = (
            f"📋 **Chat Information**\n\n"
            f"💬 Name: {chat.title}\n"
            f"🆔 ID: `{chat.id}`\n"
        )
        
        if chat.username:
            info_text += f"📱 Username: @{chat.username}\n"
        
        info_text += (
            f"👥 Members: {member_count}\n"
            f"📝 Type: {chat.type}\n"
        )
        
        if chat.description:
            info_text += f"\n📄 Description:\n{chat.description}"

        await message.reply_text(info_text)
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


# ==================== REPORT COMMAND ====================

@Client.on_message(filters.command("report", prefixes=config.COMMAND_PREFIX))
@group_only
async def report_user(client: Client, message: Message):
    """Report a message to admins"""
    try:
        # Check if replying to a message
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a message to report it")
            return
        
        # Check if reported message has a user
        if not message.reply_to_message.from_user:
            await message.reply_text("❌ Cannot report this message")
            return

        reported_user = message.reply_to_message.from_user
        
        # Extract reason safely
        reason = "No reason provided"
        try:
            if message.text and len(message.text.split()) > 1:
                reason = message.text.split(maxsplit=1)[1]
        except:
            pass
        
        # Get admins - try different filter methods
        admins = []
        try:
            # Try using ChatMembersFilter enum
            from pyrogram.enums import ChatMembersFilter
            async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if member.user and not member.user.is_bot:
                    try:
                        admins.append(member.user.mention)
                    except:
                        pass
        except ImportError:
            # Fallback to string filter for older versions
            try:
                async for member in client.get_chat_members(message.chat.id, filter="administrators"):
                    if member.user and not member.user.is_bot:
                        try:
                            admins.append(member.user.mention)
                        except:
                            pass
            except Exception as e:
                bot_logger.error(f"Error getting admins with string filter: {e}")
        except Exception as e:
            bot_logger.error(f"Error getting admins in report: {e}")

        if not admins:
            await message.reply_text("❌ No admins found to notify")
            return

        admin_mentions = " ".join(admins[:5])

        await message.reply_text(
            f"🚨 **Message Reported to Admins**\n\n"
            f"👤 Reported User: {reported_user.mention}\n"
            f"📝 Reason: {reason}\n"
            f"👮 Reported By: {message.from_user.mention}\n\n"
            f"{admin_mentions}"
        )
    except Exception as e:
        bot_logger.error(f"Error in report_user: {e}")
        try:
            await message.reply_text(f"❌ An error occurred while reporting")
        except:
            pass


# ==================== HELP COMMAND ====================

@Client.on_message(filters.command("adminhelp", prefixes=config.COMMAND_PREFIX))
@log_errors
async def admin_help(client: Client, message: Message):
    """Show all admin commands"""
    help_text = """
🛡️ **Admin Commands Help**

**Ban & Kick:**
• `/ban` - Ban a user
• `/unban` - Unban a user
• `/tban <time>` - Temp ban (e.g., 5m, 2h, 1d)
• `/kick` - Kick a user

**Mute:**
• `/mute` - Mute a user
• `/unmute` - Unmute a user
• `/tmute <time>` - Temp mute

**Warnings:**
• `/warn` - Warn a user (3 = ban)
• `/warnings` - Check warnings
• `/resetwarns` - Reset warnings

**Promote:**
• `/promote [title]` - Promote to admin (basic rights)
• `/fullpromote [title]` - Promote with all rights
• `/demote` - Demote admin

**Pin:**
• `/pin [silent]` - Pin message
• `/unpin` - Unpin message
• `/unpinall` - Unpin all

**Delete:**
• `/del` - Delete replied message
• `/purge` - Delete messages in range

**Lock:**
• `/lock` - Lock chat (admins only)
• `/unlock` - Unlock chat

**Info:**
• `/admins` - List all admins
• `/info` - User information
• `/chatinfo` - Chat information
• `/report` - Report to admins

**Usage Examples:**
• `/ban @user spam` - Ban with reason
• `/tban @user 1d` - Ban for 1 day
• `/warn @user rude` - Warn with reason
• `/promote @user Moderator` - Promote with title

**Important Notes:**
• Reply to user's message if they have no username
• Bot needs 'Add Admins' permission to promote
• `/fullpromote` gives all rights including add admins

**Time Format:**
• `s` - seconds
• `m` - minutes  
• `h` - hours
• `d` - days
• `w` - weeks
"""
    await message.reply_text(help_text)
