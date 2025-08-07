"""
Destiny 2 Discord Bot for Clan Event Management
Entry point for the bot application - Windows Version
"""

import os
import asyncio
import logging
from bot.destiny_bot import DestinyBot
from keep_alive import keep_alive

# Support pour fichier .env (pour usage Windows)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge les variables depuis le fichier .env
except ImportError:
    print("❌ python-dotenv non installé. Installez-le avec: pip install python-dotenv")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Destiny 2 bot"""
    try:
        # Démarrer le serveur keep alive
        keep_alive()
        logger.info("Keep alive server started on http://localhost:8080")
        
        # Get Discord bot token from environment variable
        bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        
        if not bot_token:
            logger.error("DISCORD_BOT_TOKEN non trouvé dans le fichier .env!")
            logger.error("Créez un fichier .env avec: DISCORD_BOT_TOKEN=votre_token_ici")
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