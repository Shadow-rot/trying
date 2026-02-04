"""
Helper Functions Module
Utility functions used across the bot
"""
import os
import time
import psutil
import humanize
from datetime import datetime, timedelta
from typing import Union
from pyrogram.types import Message


def get_readable_time(seconds: int) -> str:
    """Convert seconds to human readable time"""
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )
    
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value} {name}" if value != 1 else f"{value} {name[:-1]}")
    
    return ', '.join(result[:2]) if result else '0 seconds'


def get_readable_bytes(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    return humanize.naturalsize(size_bytes, binary=True)


def progress_bar(current: int, total: int, width: int = 20) -> str:
    """Generate a progress bar"""
    percentage = (current / total) * 100
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percentage:.1f}%"


async def progress_callback(current: int, total: int, message: Message, start_time: float, action: str = "Processing"):
    """Progress callback for file uploads/downloads"""
    now = time.time()
    diff = now - start_time
    
    if diff < 1:  # Update every second
        return
    
    percentage = (current / total) * 100
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0
    
    progress = progress_bar(current, total)
    
    text = (
        f"**{action}**\n\n"
        f"{progress}\n"
        f"**Completed:** {get_readable_bytes(current)} / {get_readable_bytes(total)}\n"
        f"**Speed:** {get_readable_bytes(int(speed))}/s\n"
        f"**ETA:** {get_readable_time(int(eta))}"
    )
    
    try:
        await message.edit_text(text)
    except Exception:
        pass


def get_system_stats() -> dict:
    """Get system statistics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used': get_readable_bytes(memory.used),
        'memory_total': get_readable_bytes(memory.total),
        'disk_percent': disk.percent,
        'disk_used': get_readable_bytes(disk.used),
        'disk_total': get_readable_bytes(disk.total)
    }


def get_uptime(start_time: float) -> str:
    """Calculate bot uptime"""
    uptime_seconds = int(time.time() - start_time)
    return get_readable_time(uptime_seconds)


def extract_args(message: Message) -> str:
    """Extract arguments from command message"""
    if not message.text:
        return ""
    
    parts = message.text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""


def extract_args_list(message: Message) -> list:
    """Extract arguments as a list"""
    args = extract_args(message)
    return args.split() if args else []


async def get_user_info(message: Message) -> dict:
    """Get user information from message"""
    user = message.from_user
    return {
        'id': user.id,
        'username': user.username or "N/A",
        'first_name': user.first_name or "N/A",
        'last_name': user.last_name or "N/A",
        'is_bot': user.is_bot,
        'is_verified': user.is_verified if hasattr(user, 'is_verified') else False,
        'is_premium': user.is_premium if hasattr(user, 'is_premium') else False
    }


def format_user_mention(user_id: int, username: str = None, first_name: str = None) -> str:
    """Format a user mention"""
    if username:
        return f"@{username}"
    elif first_name:
        return f"[{first_name}](tg://user?id={user_id})"
    else:
        return f"[User](tg://user?id={user_id})"


def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def is_url(text: str) -> bool:
    """Check if text is a valid URL"""
    return text.startswith(('http://', 'https://'))


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()


def format_date(date: datetime) -> str:
    """Format datetime to readable string"""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def parse_duration(duration_str: str) -> int:
    """Parse duration string (e.g., '1h', '30m', '45s') to seconds"""
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    try:
        if duration_str[-1] in units:
            value = int(duration_str[:-1])
            unit = duration_str[-1]
            return value * units[unit]
        else:
            return int(duration_str)
    except (ValueError, IndexError):
        return 0
