"""
Database Module
MongoDB integration for data persistence
"""
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from core.logger import bot_logger


class Database:
    """MongoDB Database Handler"""
    
    def __init__(self):
        """Initialize database connection"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.connected = False
    
    async def connect(self):
        """Connect to MongoDB"""
        if not config.ENABLE_DATABASE or not config.MONGO_URL:
            bot_logger.warning("Database is disabled or MONGO_URL not provided")
            return False
        
        try:
            self.client = AsyncIOMotorClient(config.MONGO_URL)
            self.db = self.client[config.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            self.connected = True
            bot_logger.success("✅ Connected to MongoDB")
            return True
        except Exception as e:
            bot_logger.error(f"❌ Failed to connect to MongoDB: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            bot_logger.info("Disconnected from MongoDB")
    
    # User Data Methods
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database"""
        if not self.connected:
            return None
        return await self.db.users.find_one({"user_id": user_id})
    
    async def add_user(self, user_id: int, username: str = None, **kwargs):
        """Add or update user in database"""
        if not self.connected:
            return
        
        user_data = {
            "user_id": user_id,
            "username": username,
            **kwargs
        }
        
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from database"""
        if not self.connected:
            return []
        return await self.db.users.find().to_list(length=None)
    
    # Plugin Data Methods
    async def set_data(self, collection: str, key: str, value: Any):
        """Set data in a collection"""
        if not self.connected:
            return
        
        await self.db[collection].update_one(
            {"key": key},
            {"$set": {"key": key, "value": value}},
            upsert=True
        )
    
    async def get_data(self, collection: str, key: str) -> Optional[Any]:
        """Get data from a collection"""
        if not self.connected:
            return None
        
        result = await self.db[collection].find_one({"key": key})
        return result.get("value") if result else None
    
    async def delete_data(self, collection: str, key: str):
        """Delete data from a collection"""
        if not self.connected:
            return
        
        await self.db[collection].delete_one({"key": key})
    
    # Statistics Methods
    async def increment_stat(self, stat_name: str, value: int = 1):
        """Increment a statistic"""
        if not self.connected:
            return
        
        await self.db.statistics.update_one(
            {"stat": stat_name},
            {"$inc": {"value": value}},
            upsert=True
        )
    
    async def get_stat(self, stat_name: str) -> int:
        """Get a statistic value"""
        if not self.connected:
            return 0
        
        result = await self.db.statistics.find_one({"stat": stat_name})
        return result.get("value", 0) if result else 0


# Create database instance
db = Database()
