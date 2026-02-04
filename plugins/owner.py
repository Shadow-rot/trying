"""
Owner Commands Plugin
Commands restricted to bot owner only
"""
import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from utils.decorators import log_errors, owner_only
from utils.helpers import extract_args
from core.database import db
from core.logger import bot_logger


@Client.on_message(filters.command("restart", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def restart_bot(client: Client, message: Message):
    """Restart the bot"""
    await message.reply_text("🔄 **Restarting bot...**")
    
    bot_logger.info("Bot restart requested by owner")
    
    # Save restart message info
    if db.connected:
        await db.set_data("bot_state", "restart_chat", message.chat.id)
        await db.set_data("bot_state", "restart_message", message.id)
    
    # Restart
    os.execv(sys.executable, ['python'] + sys.argv)


@Client.on_message(filters.command("shell", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def shell_command(client: Client, message: Message):
    """Execute shell commands"""
    command = extract_args(message)
    
    if not command:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}shell <command>`\n\n"
            f"⚠️ **Warning:** Be careful with shell commands!"
        )
        return
    
    status_msg = await message.reply_text(f"🖥️ **Executing:**\n`{command}`")
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        output = stdout.decode('utf-8') if stdout else ""
        error = stderr.decode('utf-8') if stderr else ""
        
        result = f"**Output:**\n```\n{output[:3000]}\n```" if output else ""
        
        if error:
            result += f"\n\n**Error:**\n```\n{error[:1000]}\n```"
        
        if not output and not error:
            result = "✅ Command executed (no output)"
        
        await status_msg.edit_text(
            f"🖥️ **Shell Command**\n\n"
            f"**Command:** `{command}`\n"
            f"**Return Code:** `{process.returncode}`\n\n"
            f"{result}"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")


@Client.on_message(filters.command("logs", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def get_logs(client: Client, message: Message):
    """Get bot logs"""
    args = extract_args(message)
    lines = 50
    
    try:
        if args and args.isdigit():
            lines = int(args)
            lines = min(lines, 200)  # Max 200 lines
    except:
        pass
    
    try:
        # Get latest log file
        log_dir = "logs"
        if not os.path.exists(log_dir):
            await message.reply_text("❌ No logs found")
            return
        
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if not log_files:
            await message.reply_text("❌ No log files found")
            return
        
        latest_log = max([os.path.join(log_dir, f) for f in log_files], key=os.path.getctime)
        
        # Read last N lines
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            log_lines = f.readlines()
            last_lines = log_lines[-lines:]
            log_text = ''.join(last_lines)
        
        # Send as file if too long
        if len(log_text) > 4000:
            await message.reply_document(
                latest_log,
                caption=f"📄 **Bot Logs** (Last {lines} lines)"
            )
        else:
            await message.reply_text(
                f"📋 **Bot Logs** (Last {lines} lines)\n\n"
                f"```\n{log_text}\n```"
            )
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")


@Client.on_message(filters.command("broadcast", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def broadcast_message(client: Client, message: Message):
    """Broadcast message to all users"""
    if not db.connected:
        await message.reply_text("❌ Database is not connected. Cannot broadcast.")
        return
    
    broadcast_msg = extract_args(message)
    
    if not broadcast_msg and not message.reply_to_message:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}broadcast <message>`\n"
            f"Or reply to a message with `{config.COMMAND_PREFIX}broadcast`"
        )
        return
    
    # Get message to broadcast
    if message.reply_to_message:
        msg_to_forward = message.reply_to_message
    else:
        msg_to_forward = None
    
    # Get all users
    users = await db.get_all_users()
    
    if not users:
        await message.reply_text("❌ No users found in database")
        return
    
    status_msg = await message.reply_text(
        f"📢 **Broadcasting to {len(users)} users...**"
    )
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            if msg_to_forward:
                await msg_to_forward.forward(user['user_id'])
            else:
                await client.send_message(user['user_id'], broadcast_msg)
            success += 1
        except Exception:
            failed += 1
        
        # Update status every 10 users
        if (success + failed) % 10 == 0:
            await status_msg.edit_text(
                f"📢 **Broadcasting...**\n\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}\n"
                f"📊 Progress: {success + failed}/{len(users)}"
            )
    
    await status_msg.edit_text(
        f"📢 **Broadcast Complete**\n\n"
        f"✅ **Success:** {success}\n"
        f"❌ **Failed:** {failed}\n"
        f"📊 **Total:** {len(users)}"
    )


@Client.on_message(filters.command("eval", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def eval_code(client: Client, message: Message):
    """Evaluate Python code"""
    code = extract_args(message)
    
    if not code:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}eval <python_code>`\n\n"
            f"⚠️ **Warning:** This executes Python code!"
        )
        return
    
    try:
        result = eval(code)
        await message.reply_text(
            f"🐍 **Python Eval**\n\n"
            f"**Code:**\n```python\n{code}\n```\n\n"
            f"**Result:**\n```python\n{result}\n```"
        )
    except Exception as e:
        await message.reply_text(
            f"🐍 **Python Eval**\n\n"
            f"**Code:**\n```python\n{code}\n```\n\n"
            f"**Error:**\n```\n{str(e)}\n```"
        )


@Client.on_message(filters.command("stats_db", prefixes=config.COMMAND_PREFIX))
@owner_only
@log_errors
async def database_stats(client: Client, message: Message):
    """Get database statistics"""
    if not db.connected:
        await message.reply_text("❌ Database is not connected")
        return
    
    try:
        users = await db.get_all_users()
        
        # Get collection stats
        collections = await db.db.list_collection_names()
        
        stats_text = "📊 **Database Statistics**\n\n"
        stats_text += f"**Users:** {len(users)}\n"
        stats_text += f"**Collections:** {len(collections)}\n\n"
        stats_text += "**Collection Names:**\n"
        
        for col in collections:
            count = await db.db[col].count_documents({})
            stats_text += f"• {col}: {count} documents\n"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")
