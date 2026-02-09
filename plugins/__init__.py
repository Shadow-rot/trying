"""
Plugins Module
Contains all bot command plugins
"""

# This file can be empty - Pyrogram will auto-discover plugins
# But we can list available plugins here for documentation

AVAILABLE_PLUGINS = [
    'help',       # Help and start commands
    'basic',      # Ping, alive, stats, info
    'admin',      # Ban, mute, kick, promote, demote
    'utilities',  # Calc, weather, translate
    'owner',      # Restart, broadcast, shell, logs
]

__all__ = ['AVAILABLE_PLUGINS']
