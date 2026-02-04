"""
Admin Commands Plugin
Group administration commands (ban, mute, kick, promote, etc.)
IMPORTANT: These commands work within Telegram's official permissions system
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, RPCError
from config import config
from utils.decorators import log_errors, admin_only, group_only
from utils.helpers import extract_args


async def get_user_from_message(client: Client, message: Message):
    """Extract user from replied message or username/ID"""
    if message.reply_to_message:
        return message.reply_to_message.from_user
    
    args = extract_args(message)
    if not args:
        await message.reply_text("❌ Reply to a user or provide username/ID")
        return None
    
    try:
        # Try to get user by username or ID
        user = await client.get_users(args)
        return user
    except Exception as e:
        await message.reply_text(f"❌ Could not find user: {e}")
        return None


@Client.on_message(filters.command("ban", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def ban_user(client: Client, message: Message):
    """Ban a user from the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return
    
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.reply_text(
            f"🚫 **User Banned**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`"
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
            f"🆔 ID: `{user.id}`"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unban users")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("kick", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def kick_user(client: Client, message: Message):
    """Kick a user from the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return
    
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply_text(
            f"👢 **User Kicked**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to kick users")
    except UserAdminInvalid:
        await message.reply_text("❌ Cannot kick administrators")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("mute", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def mute_user(client: Client, message: Message):
    """Mute a user in the group"""
    user = await get_user_from_message(client, message)
    if not user:
        return
    
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions()
        )
        await message.reply_text(
            f"🔇 **User Muted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`"
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
                can_add_web_page_previews=True
            )
        )
        await message.reply_text(
            f"🔊 **User Unmuted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to unmute users")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("promote", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def promote_user(client: Client, message: Message):
    """Promote a user to admin"""
    user = await get_user_from_message(client, message)
    if not user:
        return
    
    try:
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=ChatPermissions(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await message.reply_text(
            f"⬆️ **User Promoted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"✅ Now has admin privileges"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to promote users")
    except RPCError as e:
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
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=ChatPermissions()
        )
        await message.reply_text(
            f"⬇️ **User Demoted**\n"
            f"👤 User: {user.mention}\n"
            f"🆔 ID: `{user.id}`\n"
            f"❌ Admin privileges removed"
        )
    except ChatAdminRequired:
        await message.reply_text("❌ I need admin rights to demote users")
    except RPCError as e:
        await message.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("pin", prefixes=config.COMMAND_PREFIX))
@group_only
@admin_only
@log_errors
async def pin_message(client: Client, message: Message):
    """Pin a message"""
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to pin it")
        return
    
    try:
        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id
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
