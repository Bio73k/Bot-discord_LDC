"""
Destiny 2 Discord Bot for Clan Event Management
Entry point for the bot application
"""

import os
import asyncio
import logging
from bot.destiny_bot import DestinyBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Destiny 2 bot"""
    try:
        # Get Discord bot token from environment variable
        bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        
        if not bot_token:
            logger.error("DISCORD_BOT_TOKEN environment variable not found!")
            logger.error("Please set your Discord bot token in the environment variables.")
            return
        
        # Create and start the bot
        bot = DestinyBot()
        logger.info("Starting Destiny 2 Clan Event Bot...")
        
        await bot.start(bot_token)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        logger.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
