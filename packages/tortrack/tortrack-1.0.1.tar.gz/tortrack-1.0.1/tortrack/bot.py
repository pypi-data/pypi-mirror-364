import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .handlers import setup_handlers
from .database import Database
from .tor_proxy import TorManager

class TelegramBot:
    """
    Main bot class - just give it a token and it works!
    """
    
    def __init__(self, token: str, use_tor: bool = True, mongo_uri: str = None):
        self.token = token
        self.use_tor = use_tor
        self.mongo_uri = mongo_uri or "mongodb://localhost:27017/tortrack"
        
        # basic setup
        self.bot = None
        self.dp = None
        self.db = None
        self.tor_manager = None
        
        # setup logging for normal users
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def setup(self):
        """Internal setup - users don't need to call this"""
        try:
            # create bot instance
            self.bot = Bot(
                token=self.token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            self.dp = Dispatcher()
            
            # setup database
            self.db = Database(self.mongo_uri)
            await self.db.init()
            
            # setup tor if enabled
            if self.use_tor:
                self.tor_manager = TorManager()
                await self.tor_manager.start()
                self.logger.info("Tor anonymity enabled ✓")
            
            # setup message handlers
            setup_handlers(self.dp, self.db, self.tor_manager)
            
            self.logger.info(f"Bot initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            raise
    
    async def cleanup(self):
        """Clean shutdown"""
        try:
            if self.db:
                await self.db.close()
            if self.tor_manager:
                await self.tor_manager.stop()
            self.logger.info("Bot stopped cleanly")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def run(self):
        """
        Start the bot - this is all users need to call!
        """
        async def main():
            try:
                await self.setup()
                self.logger.info("Starting bot...")
                await self.dp.start_polling(self.bot)
            except KeyboardInterrupt:
                self.logger.info("Bot stopped by user")
            except Exception as e:
                self.logger.error(f"Bot error: {e}")
            finally:
                await self.cleanup()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.logger.info("Goodbye!")
    
    # convenience method for advanced users
    async def send_message(self, chat_id: int, text: str):
        """Send a message - useful for custom integrations"""
        if self.bot:
            await self.bot.send_message(chat_id, text)