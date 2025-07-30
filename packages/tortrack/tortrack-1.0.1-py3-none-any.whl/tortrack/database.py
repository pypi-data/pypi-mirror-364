import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

class Database:
    """
    Simple database wrapper - handles user limits and track archiving
    """
    
    def __init__(self, mongo_uri: str):
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
    
    async def init(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client.get_default_database()
            
            # test connection
            await self.client.admin.command('ping')
            self.logger.info("Database connected successfully")
            
            # create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            self.logger.warning(f"Database connection failed: {e}")
            self.logger.info("Running without database (no limits/archiving)")
            self.db = None
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    async def _create_indexes(self):
        """Create database indexes"""
        if not self.db:
            return
            
        try:
            # user downloads index
            await self.db.users.create_index([("user_id", 1)], unique=True)
            
            # archived tracks index
            await self.db.archived_tracks.create_index([("spotify_id", 1)], unique=True)
            
            # vip users index
            await self.db.vip_users.create_index([("user_id", 1)], unique=True)
            
        except Exception as e:
            self.logger.debug(f"Index creation warning: {e}")
    
    async def get_user_downloads_today(self, user_id: int) -> int:
        """Get user's download count for today"""
        if not self.db:
            return 0
            
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            user = await self.db.users.find_one({"user_id": user_id})
            
            if not user:
                return 0
            
            # reset count if it's a new day
            last_download = user.get("last_download_date")
            if not last_download or last_download < today:
                await self.db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"downloads_today": 0, "last_download_date": datetime.now()}}
                )
                return 0
            
            return user.get("downloads_today", 0)
            
        except Exception as e:
            self.logger.error(f"Database error getting downloads: {e}")
            return 0
    
    async def increment_user_downloads(self, user_id: int):
        """Increment user's download count"""
        if not self.db:
            return
            
        try:
            await self.db.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"downloads_today": 1, "total_downloads": 1},
                    "$set": {"last_download_date": datetime.now()},
                    "$setOnInsert": {"first_seen": datetime.now()}
                },
                upsert=True
            )
        except Exception as e:
            self.logger.error(f"Database error incrementing downloads: {e}")
    
    async def is_vip_user(self, user_id: int) -> bool:
        """Check if user has VIP status"""
        if not self.db:
            return False
            
        try:
            vip = await self.db.vip_users.find_one({"user_id": user_id})
            if not vip:
                return False
            
            # check if VIP is still valid
            if vip.get("expires_at", datetime.now()) > datetime.now():
                return True
            else:
                # expired VIP
                await self.db.vip_users.delete_one({"user_id": user_id})
                return False
                
        except Exception as e:
            self.logger.error(f"Database error checking VIP: {e}")
            return False
    
    async def is_track_archived(self, spotify_id: str) -> str | None:
        """Check if track was already downloaded - returns file_id if found"""
        if not self.db:
            return None
            
        try:
            track = await self.db.archived_tracks.find_one({"spotify_id": spotify_id})
            return track.get("file_id") if track else None
        except Exception as e:
            self.logger.error(f"Database error checking archive: {e}")
            return None
    
    async def archive_track(self, spotify_id: str, file_id: str, track_info: dict):
        """Save downloaded track to archive"""
        if not self.db:
            return
            
        try:
            await self.db.archived_tracks.update_one(
                {"spotify_id": spotify_id},
                {
                    "$set": {
                        "file_id": file_id,
                        "track_info": track_info,
                        "archived_at": datetime.now()
                    }
                },
                upsert=True
            )
        except Exception as e:
            self.logger.error(f"Database error archiving track: {e}")
    
    async def get_stats(self) -> dict:
        """Get basic stats - useful for admin"""
        if not self.db:
            return {"error": "No database connected"}
            
        try:
            total_users = await self.db.users.count_documents({})
            total_tracks = await self.db.archived_tracks.count_documents({})
            vip_users = await self.db.vip_users.count_documents({})
            
            return {
                "total_users": total_users,
                "total_tracks": total_tracks,
                "vip_users": vip_users
            }
        except Exception as e:
            self.logger.error(f"Database error getting stats: {e}")
            return {"error": str(e)}