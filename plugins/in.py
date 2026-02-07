"""
Inline Buttons Demo - COLORED BUTTONS (Layer 224)
Shows actual colored inline buttons using new MTProto schema
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.types import (
    ReplyInlineMarkup,
    KeyboardButtonUrl,
    KeyboardButtonCallback,
    KeyboardButtonStyle
)
from config import config
from utils.decorators import log_errors


@Client.on_message(filters.command("inline", prefixes=config.COMMAND_PREFIX))
@log_errors
async def show_inline_buttons(client: Client, message: Message):
    """Display colored inline buttons (Layer 224)"""
    
    # Create button styles
    style_primary = KeyboardButtonStyle(bg_primary=True)
    style_success = KeyboardButtonStyle(bg_success=True)
    style_danger = KeyboardButtonStyle(bg_danger=True)
    
    # Create keyboard with colored buttons
    keyboard = ReplyInlineMarkup(
        rows=[
            [
                KeyboardButtonCallback(
                    text="OwO",
                    data=b"primary",
                    style=style_primary
                )
            ],
            [
                KeyboardButtonCallback(
                    text="UwU",
                    data=b"danger",
                    style=style_danger
                )
            ],
            [
                KeyboardButtonCallback(
                    text="💚 Success",
                    data=b"success",
                    style=style_success
                )
            ]
        ]
    )
    
    await message.reply(
        "This is a Inline keyboard",
        reply_markup=keyboard
    )



@Client.on_callback_query(filters.regex(r"^(primary|danger|success)$"))
@log_errors
async def handle_inline_callback(client: Client, callback_query):
    """Handle button clicks"""
    button_type = callback_query.data.decode()
    await callback_query.answer(f"You clicked: {button_type} button!", show_alert=True)