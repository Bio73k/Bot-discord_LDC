"""
Main Discord bot class for Destiny 2 clan event management
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
from bot.commands.event_commands import EventCommands
from bot.commands.team_commands import TeamCommands
from services.event_service import EventService
from services.team_service import TeamService
from services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

class DestinyBot(commands.Bot):
    """Main bot class for Destiny 2 clan events"""
    
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(
            command_prefix='!',  # Keep for fallback, but we'll use slash commands
            intents=intents,
            help_command=None
        )
        
        # Initialize services
        self.event_service = EventService()
        self.team_service = TeamService()
        self.reminder_service = ReminderService(self, self.event_service)
        
        # Event feed channel storage (guild_id -> channel_id)
        self.event_feed_channels = {}
        
    async def setup_hook(self):
        """Set up the bot when it starts"""
        try:
            # Add cogs (command groups)
            await self.add_cog(EventCommands(self))
            await self.add_cog(TeamCommands(self))
            
            logger.info("Bot cogs loaded successfully")
            
            # Sync slash commands
            await self.tree.sync()
            logger.info("Slash commands synced successfully")
            
        except Exception as e:
            logger.error(f"Failed to load cogs or sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="les événements du clan Destiny 2 | /events"
        )
        await self.change_presence(activity=activity)
        
        # Start reminder service
        await self.reminder_service.start()
    
    async def create_event_thread(self, event, channel, ping_role_name: Optional[str] = None):
        """Create a thread for the event in the specified channel"""
        try:
            if channel:
                    # Create thread for the event
                    thread_name = f"{event.event_type.value}: {event.name}"
                    if len(thread_name) > 100:  # Discord thread name limit
                        thread_name = thread_name[:97] + "..."
                    
                    thread = await channel.create_thread(
                        name=thread_name,
                        type=discord.ChannelType.public_thread,
                        reason=f"Event thread for {event.name}"
                    )
                    
                    # Send initial message to the thread
                    from utils.embeds import EventEmbeds
                    
                    embed = discord.Embed(
                        title=f"🎯 {event.name}",
                        description=event.description or "Aucune description fournie",
                        color=0x00ff00
                    )
                    
                    embed.add_field(
                        name="Type d'événement",
                        value=event.event_type.value,
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Participants max",
                        value=f"{event.max_participants} joueurs",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="ID événement",
                        value=f"`{event.event_id}`",
                        inline=True
                    )
                    

                    

                    
                    # Create welcome message with optional role ping
                    welcome_msg = f"Bienvenue dans le fil de discussion de l'événement **{event.name}** ! 🎉\n\nC'est ici que vous pouvez discuter de stratégies, vous coordonner et parler de cet événement."
                    
                    # Add role ping if specified
                    if ping_role_name and channel.guild:
                        role = discord.utils.get(channel.guild.roles, name=ping_role_name)
                        if role:
                            welcome_msg = f"{role.mention} {welcome_msg}"
                    
                    await thread.send(welcome_msg, embed=embed)
                    
                    # Store thread ID in event for future reference
                    event.thread_id = thread.id
                    
                    return thread
                    
        except Exception as e:
            logger.error(f"Failed to create event thread: {e}")
            return None
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            # Suggest similar commands instead of just saying "use !help"
            suggestions = [
                "Try using slash commands like `/create-event` or `/events`",
                "For creating events: `/create-event`",
                "To see all events: `/events`",
                "For team management: `/randomize-teams`"
            ]
            await ctx.send(f"❌ Unknown command. {suggestions[0]}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send("❌ An error occurred while processing the command.")
    
    @commands.command(name='help')
    async def custom_help_command(self, ctx):
        """Display help information"""
        embed = discord.Embed(
            title="🎮 Destiny 2 Clan Event Bot",
            description="Organize your clan events with ease!",
            color=0x00bfff
        )
        
        # Event Commands
        embed.add_field(
            name="📅 Event Commands",
            value=(
                "`/create-event` - Create any type of event (Bingo, PvP, Raid, General, Custom)\n"
                "`/events` - List all active events\n"
                "`/event-info <event_id>` - Show event details\n"
                "`/join-event <event_id>` - Join an event\n"
                "`/leave-event <event_id>` - Leave an event\n"
                "Or just react with ✅ to join, ❌ to leave"
            ),
            inline=False
        )
        
        # Team Commands
        embed.add_field(
            name="⚔️ Team Commands",
            value=(
                "`/randomize-teams <event_id> <team_size>` - Create random teams\n"
                "`/show-teams <event_id>` - Display current teams\n"
                "`/clear-teams <event_id>` - Clear team assignments"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Tips",
            value=(
                "• React with ✅ to join events\n"
                "• React with ❌ to leave events\n"
                "• Events support up to 100 participants\n"
                "• Team sizes can be 2, 3, 4, or 6 players"
            ),
            inline=False
        )
        
        embed.set_footer(text="Guardian, the Traveler's light guides us!")
        
        await ctx.send(embed=embed)
