"""
Configuration Module
Handles all environment variables and bot settings
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot Configuration Class"""
    
    # Telegram API Configuration
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Bot Owner Configuration
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    SUDO_USERS: List[int] = [
        int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()
    ]
    
    # Command Configuration
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", ".")
    
    # Database Configuration
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "telegram_bot")
    
    # Logging Configuration
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL", "0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Features Toggle
    ENABLE_PLUGINS: bool = os.getenv("ENABLE_PLUGINS", "true").lower() == "true"
    ENABLE_DATABASE: bool = os.getenv("ENABLE_DATABASE", "false").lower() == "true"
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    
    # API Keys
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    DEEPL_API_KEY: str = os.getenv("DEEPL_API_KEY", "")
    
    # Performance Settings
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    FLOOD_WAIT_THRESHOLD: int = int(os.getenv("FLOOD_WAIT_THRESHOLD", "10"))
    
    # Bot Information
    BOT_NAME: str = "Advanced Telegram Bot"
    BOT_VERSION: str = "2.0.0"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = {
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "BOT_TOKEN": cls.BOT_TOKEN,
            "OWNER_ID": cls.OWNER_ID
        }
        
        missing_fields = [
            field for field, value in required_fields.items()
            if not value or (isinstance(value, int) and value == 0)
        ]
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @classmethod
    def is_owner(cls, user_id: int) -> bool:
        """Check if user is bot owner"""
        return user_id == cls.OWNER_ID
    
    @classmethod
    def is_sudo(cls, user_id: int) -> bool:
        """Check if user has sudo privileges"""
        return user_id in cls.SUDO_USERS or cls.is_owner(user_id)


# Create config instance
config = Config()
