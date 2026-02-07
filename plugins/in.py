"""
Inline Buttons Demo - COLORED BUTTONS
Requires: pip install git+https://github.com/pyrogram/pyrogram.git
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonUrl,
    KeyboardButtonStyle
)
from pyrogram.raw import functions
from config import config
from utils.decorators import log_errors


@Client.on_message(filters.command("inline", prefixes=config.COMMAND_PREFIX))
@log_errors
async def show_inline_buttons(client: Client, message: Message):
    """Display colored inline buttons"""
    
    keyboard = ReplyInlineMarkup(
        rows=[
            KeyboardButtonRow(
                buttons=[
                    KeyboardButtonUrl(
                        text="OwO",
                        url="https://t.me/I_shadwoo",
                        flags=1024,  # Enable style flag
                        style=KeyboardButtonStyle(
                            flags=1,
                            bg_primary=True
                        )
                    )
                ]
            ),
            KeyboardButtonRow(
                buttons=[
                    KeyboardButtonUrl(
                        text="UwU",
                        url="https://t.me/I_shadwoo",
                        flags=1024,
                        style=KeyboardButtonStyle(
                            flags=2,
                            bg_danger=True
                        )
                    )
                ]
            ),
            KeyboardButtonRow(
                buttons=[
                    KeyboardButtonUrl(
                        text="💚 Success",
                        url="https://t.me/I_shadwoo",
                        flags=1024,
                        style=KeyboardButtonStyle(
                            flags=4,
                            bg_success=True
                        )
                    )
                ]
            )
        ]
    )
    
    await client.invoke(
        functions.messages.SendMessage(
            peer=await client.resolve_peer(message.chat.id),
            message="This is a Inline keyboard",
            reply_markup=keyboard,
            random_id=client.rnd_id()
        )
           ) 