"""
Core Module
Contains core bot functionality
"""
from .client import bot, BotClient
from .database import db, Database
from .logger import bot_logger, BotLogger

__all__ = [
    'bot',
    'BotClient',
    'db',
    'Database',
    'bot_logger',
    'BotLogger'
]
