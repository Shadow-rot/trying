"""
plugins/inline_demo.py
Hybrid: Uses Telethon ONLY for colored buttons
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from telethon import TelegramClient
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonUrl,
    KeyboardButtonStyle
)
from config import config
from utils.decorators import log_errors

# Create Telethon client (shares same bot token)
telethon_bot = TelegramClient(
    'telethon_bot',
    api_id=config.API_ID,
    api_hash=config.API_HASH
).start(bot_token=config.BOT_TOKEN)


@Client.on_message(filters.command("inline", prefixes=config.COMMAND_PREFIX))
@log_errors
async def show_inline_buttons(client: Client, message: Message):
    """Display REAL colored buttons using Telethon"""
    
    keyboard = ReplyInlineMarkup([
        KeyboardButtonRow([
            KeyboardButtonUrl(
                text="OwO",
                url="https://t.me/I_shadwoo",
                style=KeyboardButtonStyle(bg_primary=True)
            )
        ]),
        KeyboardButtonRow([
            KeyboardButtonUrl(
                text="UwU",
                url="https://t.me/I_shadwoo",
                style=KeyboardButtonStyle(bg_danger=True)
            )
        ]),
        KeyboardButtonRow([
            KeyboardButtonUrl(
                text="💚 Success",
                url="https://t.me/I_shadwoo",
                style=KeyboardButtonStyle(bg_success=True)
            )
        ])
    ])
    
    # Use Telethon to send with colored buttons
    await telethon_bot.send_message(
        message.chat.id,
        "This is a Inline keyboard",
        buttons=keyboard
    )
    
    # Delete the command message
    await message.delete()