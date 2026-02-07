"""
Inline Buttons Demo
Shows colored inline buttons linking to t.me/I_shadwoo
"""
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from utils.decorators import log_errors


@Client.on_message(filters.command("inline", prefixes=config.COMMAND_PREFIX))
@log_errors
async def show_inline_buttons(client: Client, message: Message):
    """Display colored inline buttons"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💙 Primary",
                url="https://t.me/I_shadwoo",
                style="primary"
            )
        ],
        [
            InlineKeyboardButton(
                "💚 Success",
                url="https://t.me/I_shadwoo",
                style="success"
            )
        ],
        [
            InlineKeyboardButton(
                "❤️ Danger",
                url="https://t.me/I_shadwoo",
                style="danger"
            )
        ]
    ])
    
    await message.reply_text(
        "**Colored Inline Buttons Demo**",
        reply_markup=keyboard
    )