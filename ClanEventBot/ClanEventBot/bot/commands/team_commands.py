"""
Discord commands for team management
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.embeds import TeamEmbeds

logger = logging.getLogger(__name__)

class TeamCommands(commands.Cog):
    """Commands for managing teams in Destiny 2 events"""
    
    def __init__(self, bot):
        self.bot = bot
        self.event_service = bot.event_service
        self.team_service = bot.team_service
    
    @commands.command(name='randomize-teams')
    async def randomize_teams(self, ctx, event_id: str, team_size: int):
        """Randomize teams for an event"""
        try:
            # Validate team size
            if team_size not in [1, 2, 3, 4, 6]:
                await ctx.send("❌ Team size must be 1, 2, 3, 4, or 6 players.")
                return
            
            # Get the event
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            # Check if user can manage teams (creator or admin)
            if event.creator_id != ctx.author.id and not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Only the event creator or server administrators can randomize teams.")
                return
            
            # Check if there are participants
            if not event.participants:
                await ctx.send("❌ No participants to randomize into teams.")
                return
            
            # Randomize teams
            teams = self.team_service.randomize_teams(event.participants, team_size)
            
            if not teams:
                await ctx.send("❌ Failed to create teams. Make sure there are enough participants.")
                return
            
            # Update event with teams
            event.teams = teams
            event.team_size = team_size
            
            # Post teams only in the event thread for clarity
            if event.thread_id:
                try:
                    thread = self.bot.get_channel(event.thread_id)
                    if not thread:
                        thread = await self.bot.fetch_channel(event.thread_id)
                    if thread:
                        embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                        await thread.send("⚔️ **Équipes créées !**", embed=embed)
                        # Send confirmation in main channel
                        await ctx.send(f"✅ Équipes créées pour '{event.name}' ! Consultez le fil pour voir les compositions.")
                    else:
                        # Fallback if no thread found
                        embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                        await ctx.send(embed=embed)
                except Exception as e:
                    logger.warning(f"Failed to post teams in thread {event.thread_id}: {e}")
                    # Fallback if thread fails
                    embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                    await ctx.send(embed=embed)
            else:
                # No thread, post in channel as fallback
                embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                await ctx.send(embed=embed)
            
            logger.info(f"Randomized teams for event {event_id}: {len(teams)} teams of size {team_size}")
            
        except ValueError as e:
            await ctx.send(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Failed to randomize teams: {e}")
            await ctx.send("❌ Failed to randomize teams. Please try again.")
    
    @commands.command(name='show-teams')
    async def show_teams(self, ctx, event_id: str):
        """Display current team assignments for an event"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            if not event.teams:
                await ctx.send("❌ No teams have been created for this event yet. Use `!randomize-teams` to create teams.")
                return
            
            embed = TeamEmbeds.create_teams_embed(event, event.teams, self.bot)
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to show teams: {e}")
            await ctx.send("❌ Failed to display teams.")
    
    @commands.command(name='clear-teams')
    async def clear_teams(self, ctx, event_id: str):
        """Clear all team assignments for an event"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            # Check if user can manage teams (creator or admin)
            if event.creator_id != ctx.author.id and not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Only the event creator or server administrators can clear teams.")
                return
            
            # Clear teams
            event.teams = []
            event.team_size = None
            
            embed = discord.Embed(
                title="🧹 Teams Cleared",
                description=f"All team assignments for '{event.name}' have been cleared.",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
            logger.info(f"Cleared teams for event {event_id}")
            
        except Exception as e:
            logger.error(f"Failed to clear teams: {e}")
            await ctx.send("❌ Failed to clear teams.")
    
    @commands.command(name='team-stats')
    async def team_stats(self, ctx, event_id: str):
        """Show team statistics for an event"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            if not event.teams:
                await ctx.send("❌ No teams have been created for this event yet.")
                return
            
            # Calculate stats
            total_teams = len(event.teams)
            total_players = sum(len(team) for team in event.teams)
            unassigned_players = len(event.participants) - total_players
            
            embed = discord.Embed(
                title="📊 Team Statistics",
                description=f"Statistics for '{event.name}'",
                color=0x00bfff
            )
            
            embed.add_field(
                name="Team Information",
                value=(
                    f"**Total Teams:** {total_teams}\n"
                    f"**Team Size:** {event.team_size}\n"
                    f"**Players in Teams:** {total_players}\n"
                    f"**Unassigned Players:** {unassigned_players}"
                ),
                inline=False
            )
            
            if unassigned_players > 0:
                embed.add_field(
                    name="⚠️ Note",
                    value=f"{unassigned_players} player(s) couldn't be assigned to teams due to team size constraints.",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to show team stats: {e}")
            await ctx.send("❌ Failed to display team statistics.")
    
    # === SLASH COMMANDS ===
    
    @app_commands.command(name="randomize-teams", description="Randomize teams for an event")
    @app_commands.describe(
        event_id="The ID of the event to create teams for",
        team_size="Number of players per team (2, 3, 4, or 6)"
    )
    @app_commands.choices(team_size=[
        app_commands.Choice(name="1 player (Solo)", value=1),
        app_commands.Choice(name="2 players", value=2),
        app_commands.Choice(name="3 players", value=3),
        app_commands.Choice(name="4 players", value=4),
        app_commands.Choice(name="6 players", value=6)
    ])
    async def slash_randomize_teams(self, interaction: discord.Interaction, event_id: str, team_size: int):
        """Randomize teams using slash commands"""
        try:
            # Get the event
            event = self.event_service.get_event(event_id)
            
            if not event:
                await interaction.response.send_message("❌ Event not found.", ephemeral=True)
                return
            
            if event.guild_id != interaction.guild_id:
                await interaction.response.send_message("❌ Event not found in this server.", ephemeral=True)
                return
            
            # Check if user can manage teams (creator only for now)
            if event.creator_id != interaction.user.id:
                await interaction.response.send_message("❌ Only the event creator can randomize teams.", ephemeral=True)
                return
            
            # Check if there are participants
            if not event.participants:
                await interaction.response.send_message("❌ No participants to randomize into teams.", ephemeral=True)
                return
            
            # Randomize teams
            teams = self.team_service.randomize_teams(event.participants, team_size)
            
            if not teams:
                await interaction.response.send_message("❌ Failed to create teams. Make sure there are enough participants.", ephemeral=True)
                return
            
            # Update event with teams
            event.teams = teams
            event.team_size = team_size
            
            # Post teams only in the event thread for clarity
            if event.thread_id:
                try:
                    thread = self.bot.get_channel(event.thread_id)
                    if not thread:
                        thread = await self.bot.fetch_channel(event.thread_id)
                    if thread:
                        embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                        await thread.send("⚔️ **Équipes créées !**", embed=embed)
                        # Send confirmation in main channel
                        await interaction.response.send_message(f"✅ Équipes créées pour '{event.name}' ! Consultez le fil pour voir les compositions.", ephemeral=True)
                    else:
                        # Fallback if no thread found
                        embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                        await interaction.response.send_message(embed=embed)
                except Exception as e:
                    logger.warning(f"Failed to post teams in thread {event.thread_id}: {e}")
                    # Fallback if thread fails
                    embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                    await interaction.response.send_message(embed=embed)
            else:
                # No thread, post in channel as fallback
                embed = TeamEmbeds.create_teams_embed(event, teams, self.bot)
                await interaction.response.send_message(embed=embed)
            
            logger.info(f"Randomized teams for event {event_id}: {len(teams)} teams of size {team_size}")
            
        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to randomize teams via slash command: {e}")
            await interaction.response.send_message("❌ Failed to randomize teams. Please try again.", ephemeral=True)
    
    @app_commands.command(name="show-teams", description="Display current team assignments for an event")
    @app_commands.describe(event_id="The ID of the event to show teams for")
    async def slash_show_teams(self, interaction: discord.Interaction, event_id: str):
        """Show teams using slash commands"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await interaction.response.send_message("❌ Event not found.", ephemeral=True)
                return
            
            if event.guild_id != interaction.guild_id:
                await interaction.response.send_message("❌ Event not found in this server.", ephemeral=True)
                return
            
            if not event.teams:
                await interaction.response.send_message("❌ No teams have been created for this event yet. Use `/randomize-teams` to create teams.", ephemeral=True)
                return
            
            embed = TeamEmbeds.create_teams_embed(event, event.teams, self.bot)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to show teams via slash command: {e}")
            await interaction.response.send_message("❌ Failed to display teams.", ephemeral=True)
    
    @app_commands.command(name="clear-teams", description="Clear all team assignments for an event")
    @app_commands.describe(event_id="The ID of the event to clear teams for")
    async def slash_clear_teams(self, interaction: discord.Interaction, event_id: str):
        """Clear teams using slash commands"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await interaction.response.send_message("❌ Event not found.", ephemeral=True)
                return
            
            if event.guild_id != interaction.guild_id:
                await interaction.response.send_message("❌ Event not found in this server.", ephemeral=True)
                return
            
            # Check if user can manage teams (creator only for now)
            if event.creator_id != interaction.user.id:
                await interaction.response.send_message("❌ Only the event creator can clear teams.", ephemeral=True)
                return
            
            # Clear teams
            event.teams = []
            event.team_size = None
            
            embed = discord.Embed(
                title="🧹 Teams Cleared",
                description=f"All team assignments for '{event.name}' have been cleared.",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Cleared teams for event {event_id}")
            
        except Exception as e:
            logger.error(f"Failed to clear teams via slash command: {e}")
            await interaction.response.send_message("❌ Failed to clear teams.", ephemeral=True)
