import asyncio
import logging
from pyrogram import Client, idle
from config import Config
from database.mongodb import Database
from bot.handlers import register_handlers
from bot.handlers.notifications import init_notifications

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LinkBypasserBot:
    def __init__(self):
        self.app = None
        self.db = None
        self.notification_system = None
        
    async def start(self):
        """Initialize and start the bot"""
        try:
            # Validate configuration
            Config.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize database
            self.db = Database()
            await self.db.connect()
            logger.info("Database connected successfully")
            
            # Initialize Pyrogram client
            self.app = Client(
                "link_bypasser_bot",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN,
                plugins=dict(root="bot/handlers"),
                workdir="."
            )
            
            # Register handlers
            register_handlers(self.app)
            logger.info("Handlers registered successfully")
            
            # Start the bot
            await self.app.start()
            logger.info("Bot started successfully!")
            
            # Get bot information
            me = await self.app.get_me()
            logger.info(f"Bot running as @{me.username}")
            
            # Initialize and start notification system
            self.notification_system = init_notifications(self.app)
            await self.notification_system.start()
            logger.info("Notification system initialized")
            
            # Setup webhook or polling
            if Config.USE_WEBHOOK and Config.WEBHOOK_URL:
                # Set webhook
                webhook_url = f"{Config.WEBHOOK_URL}/webhook"
                await self.app.set_webhook(webhook_url)
                logger.info(f"Webhook set to: {webhook_url}")
            else:
                logger.info("Using polling mode")
            
            # Send startup message to log channel
            if Config.LOG_CHANNEL:
                try:
                    await self.app.send_message(
                        Config.LOG_CHANNEL,
                        "🟢 **Bot Started Successfully!**\n\n"
                        f"**Bot:** @{me.username}\n"
                        f"**Status:** Online\n"
                        f"**Mode:** {'Groups Only' if Config.WORK_IN_GROUPS_ONLY else 'Groups & PM'}"
                    )
                except Exception as e:
                    logger.error(f"Failed to send startup message: {e}")
            
            # Keep the bot running
            await idle()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
        
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            # Stop notification system
            if self.notification_system:
                await self.notification_system.stop()
                logger.info("Notification system stopped")
            
            if self.app:
                # Send shutdown message
                if Config.LOG_CHANNEL:
                    try:
                        await self.app.send_message(
                            Config.LOG_CHANNEL,
                            "🔴 **Bot Shutting Down...**"
                        )
                    except:
                        pass
                
                await self.app.stop()
                logger.info("Bot stopped")
            
            if self.db:
                await self.db.close()
                logger.info("Database connection closed")
                
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

async def main():
    """Main entry point"""
    bot = LinkBypasserBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
