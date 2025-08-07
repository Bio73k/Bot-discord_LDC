"""
Discord commands for event management
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.embeds import EventEmbeds
from utils.constants import EventType, EventStatus
from utils.event_creation_modal import EventTypeSelectView

logger = logging.getLogger(__name__)

class EventCommands(commands.Cog):
    """Commands for managing Destiny 2 clan events"""
    
    def __init__(self, bot):
        self.bot = bot
        self.event_service = bot.event_service
    
    @commands.command(name='create-bingo')
    async def create_bingo_event(self, ctx, name: str, *, description: str = ""):
        """Create a new Bingo event"""
        await self._create_event(ctx, EventType.BINGO, name, description)
    
    @commands.command(name='create-pvp')
    async def create_pvp_event(self, ctx, name: str, *, description: str = ""):
        """Create a new PvP Tournament event"""
        await self._create_event(ctx, EventType.PVP_TOURNAMENT, name, description)
    
    
    @commands.command(name='create-general')
    async def create_general_event(self, ctx, name: str, *, description: str = ""):
        """Create a new General event"""
        await self._create_event(ctx, EventType.GENERAL, name, description)
    
    @commands.command(name='test-reminder')
    async def test_reminder(self, ctx):
        """Create a test event in 2 minutes to verify reminder system"""
        from datetime import datetime, timedelta
        from utils.embeds import EventEmbeds
        from utils.event_buttons import EventParticipationView
        
        try:
            # Create event in 2 minutes
            from utils.timezone_utils import get_france_time, format_french_datetime
            
            now = datetime.utcnow()
            test_time = now + timedelta(minutes=2)
            
            france_now = get_france_time()
            
            event = self.event_service.create_event(
                event_type=EventType.GENERAL,
                name="Test Rappel",
                description=f"Événement test pour vérifier le système de rappel. Créé à {france_now.strftime('%H:%M:%S')} (heure française), prévu dans 2 minutes",
                creator_id=ctx.author.id,
                guild_id=ctx.guild.id,
                max_participants=100,
                event_date=test_time,
                team_size=1
            )
            
            # Create embed and buttons
            embed = EventEmbeds.create_event_embed(event, self.bot)
            view = EventParticipationView(event.event_id, self.event_service, self.bot)
            
            # Send message
            message = await ctx.send("🧪 **Test du système de rappel**\n\nÉvénement créé dans 2 minutes pour tester les rappels:", embed=embed, view=view)
            
            # Store message info
            event.message_id = message.id
            self.event_service.link_message_to_event(message.id, event.event_id)
            
            # Create thread
            try:
                thread = await message.create_thread(
                    name=f"🧵 Test Rappel",
                    auto_archive_duration=4320,
                    reason="Thread de test pour le système de rappel"
                )
                event.thread_id = thread.id
                
                french_time = format_french_datetime(test_time)
                await thread.send(f"<@&1348280452305260554> Thread de test créé ! Le rappel devrait arriver dans ~2 minutes.\n\nÉvénement programmé à **{french_time}** (heure française).")
                
            except Exception as e:
                logger.error(f"Failed to create test thread: {e}")
            
            logger.info(f"Created test reminder event: {event.event_id} scheduled for {test_time}")
            
        except Exception as e:
            logger.error(f"Error creating test reminder event: {e}")
            await ctx.send("❌ Erreur lors de la création de l'événement test.")
    
    async def _create_event(self, ctx, event_type: EventType, name: str, description: str):
        """Helper method to create an event"""
        try:
            # Create the event
            event = self.event_service.create_event(
                event_type=event_type,
                name=name,
                description=description,
                creator_id=ctx.author.id,
                guild_id=ctx.guild.id
            )
            
            # Create and send embed
            embed = EventEmbeds.create_event_embed(event)
            message = await ctx.send(embed=embed)
            
            # Add reactions for joining/leaving
            await message.add_reaction("🎮")  # Participer
            await message.add_reaction("🚪")  # Ne plus participer
            
            # Store message ID for reaction handling
            event.message_id = message.id
            
            logger.info(f"Created {event_type.value} event: {name} (ID: {event.event_id})")
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            await ctx.send("❌ Failed to create event. Please try again.")
    
    @commands.command(name='events')
    async def list_events(self, ctx):
        """List all active events in the server"""
        try:
            events = self.event_service.get_events_by_guild(ctx.guild.id)
            
            if not events:
                embed = discord.Embed(
                    title="📅 Active Events",
                    description="No active events found. Create one with `!create-<type> <name> <description>`",
                    color=0x888888
                )
                await ctx.send(embed=embed)
                return
            
            embed = EventEmbeds.create_events_list_embed(events)
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            await ctx.send("❌ Failed to retrieve events. Please try again.")
    
    @commands.command(name='event-info')
    async def event_info(self, ctx, event_id: str):
        """Show detailed information about an event"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            embed = EventEmbeds.create_event_detail_embed(event, self.bot)
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to get event info: {e}")
            await ctx.send("❌ Failed to retrieve event information.")
    
    @commands.command(name='delete-event')
    async def delete_event(self, ctx, event_id: str):
        """Delete an event (only creator or admin can delete)"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            # Check permissions
            if event.creator_id != ctx.author.id and not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Only the event creator or server administrators can delete events.")
                return
            
            # Delete the event
            if self.event_service.delete_event(event_id):
                embed = discord.Embed(
                    title="🗑️ Event Deleted",
                    description=f"Event '{event.name}' has been deleted.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to delete event.")
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            await ctx.send("❌ Failed to delete event.")
    
    @commands.command(name='clear-events')
    async def clear_events(self, ctx):
        """Clear all events in this server"""
        try:
            
            # Get events for this guild
            guild_events = [event for event in self.event_service._events.values() 
                          if event.guild_id == ctx.guild.id]
            
            if not guild_events:
                await ctx.send("❌ No events found in this server.")
                return
            
            # Clear events
            cleared_count = 0
            for event in guild_events:
                if self.event_service.delete_event(event.event_id):
                    cleared_count += 1
            
            embed = discord.Embed(
                title="🧹 Events Cleared",
                description=f"Successfully cleared {cleared_count} event(s) from this server.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"User {ctx.author.id} cleared {cleared_count} events from guild {ctx.guild.id}")
                
        except Exception as e:
            logger.error(f"Failed to clear events: {e}")
            await ctx.send("❌ An error occurred while clearing events.")
    
    @commands.command(name='join-event')
    async def join_event(self, ctx, event_id: str):
        """Join an event"""
        await self._handle_event_participation(ctx, event_id, True)
    
    @commands.command(name='leave-event')
    async def leave_event(self, ctx, event_id: str):
        """Leave an event"""
        await self._handle_event_participation(ctx, event_id, False)
    
    async def _handle_event_participation(self, ctx, event_id: str, join: bool):
        """Helper method to handle joining/leaving events"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await ctx.send("❌ Event not found.")
                return
            
            if event.guild_id != ctx.guild.id:
                await ctx.send("❌ Event not found in this server.")
                return
            
            if join:
                success = self.event_service.add_participant(event_id, ctx.author.id)
                action = "joined" if success else "failed to join"
                emoji = "✅" if success else "❌"
            else:
                success = self.event_service.remove_participant(event_id, ctx.author.id)
                action = "left" if success else "failed to leave"
                emoji = "❌" if success else "❌"
            
            if success:
                await ctx.send(f"{emoji} You have {action} the event '{event.name}'.")
            else:
                if join:
                    await ctx.send("❌ Failed to join event. You might already be in it or it's full.")
                else:
                    await ctx.send("❌ Failed to leave event. You might not be in it.")
            
        except Exception as e:
            logger.error(f"Failed to handle event participation: {e}")
            await ctx.send("❌ An error occurred while processing your request.")
    
    # === SLASH COMMANDS ===
    
    @app_commands.command(name="create-event-interactive", description="Créer un événement avec une interface interactive")
    async def slash_create_event_interactive(self, interaction: discord.Interaction):
        """Create an event using interactive interface"""
        try:
            # Create the initial embed
            embed = discord.Embed(
                title="📅 Création d'événement interactif",
                description=(
                    f"Salut <@{interaction.user.id}> !\n\n"
                    f"🎯 **Étape 1/2 :** Choisissez le type d'événement\n"
                    f"📝 **Étape 2/2 :** Remplissez les détails (nom, date, heure, taille d'équipe)\n\n"
                    f"Utilisez le menu déroulant ci-dessous pour commencer !"
                ),
                color=0x00bfff
            )
            
            # Create the view with event type selection
            view = EventTypeSelectView(interaction.user.id)
            
            # Send the interactive message
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
            logger.info(f"Started interactive event creation for user {interaction.user.id}")
            
        except Exception as e:
            logger.error(f"Failed to start interactive event creation: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors du démarrage de l'interface interactive.",
                ephemeral=True
            )
    

    
    @app_commands.command(name="events", description="Lister tous les événements actifs du serveur")
    async def slash_list_events(self, interaction: discord.Interaction):
        """List events using slash commands"""
        try:
            events = self.event_service.get_events_by_guild(interaction.guild_id)
            
            if not events:
                embed = discord.Embed(
                    title="📅 Événements actifs",
                    description="Aucun événement actif trouvé. Créez-en un avec `/create-event`",
                    color=0x888888
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = EventEmbeds.create_events_list_embed(events)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to list events via slash command: {e}")
            await interaction.response.send_message("❌ Failed to retrieve events. Please try again.", ephemeral=True)
    
    @app_commands.command(name="event-info", description="Afficher les informations détaillées d'un événement")
    @app_commands.describe(event_id="L'ID de l'événement à voir")
    async def slash_event_info(self, interaction: discord.Interaction, event_id: str):
        """Show event info using slash commands"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await interaction.response.send_message("❌ Event not found.", ephemeral=True)
                return
            
            if event.guild_id != interaction.guild_id:
                await interaction.response.send_message("❌ Event not found in this server.", ephemeral=True)
                return
            
            embed = EventEmbeds.create_event_detail_embed(event, self.bot)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to get event info via slash command: {e}")
            await interaction.response.send_message("❌ Failed to retrieve event information.", ephemeral=True)
    
    @app_commands.command(name="join-event", description="Rejoindre un événement")
    @app_commands.describe(event_id="L'ID de l'événement à rejoindre")
    async def slash_join_event(self, interaction: discord.Interaction, event_id: str):
        """Join an event using slash commands"""
        await self._handle_slash_event_participation(interaction, event_id, True)
    
    @app_commands.command(name="leave-event", description="Quitter un événement")
    @app_commands.describe(event_id="L'ID de l'événement à quitter")
    async def slash_leave_event(self, interaction: discord.Interaction, event_id: str):
        """Leave an event using slash commands"""
        await self._handle_slash_event_participation(interaction, event_id, False)
    
    async def _handle_slash_event_participation(self, interaction: discord.Interaction, event_id: str, join: bool):
        """Helper method for slash command event participation"""
        try:
            event = self.event_service.get_event(event_id)
            
            if not event:
                await interaction.response.send_message("❌ Event not found.", ephemeral=True)
                return
            
            if event.guild_id != interaction.guild_id:
                await interaction.response.send_message("❌ Event not found in this server.", ephemeral=True)
                return
            
            if join:
                success = self.event_service.add_participant(event_id, interaction.user.id)
                action = "joined" if success else "failed to join"
                emoji = "✅" if success else "❌"
            else:
                success = self.event_service.remove_participant(event_id, interaction.user.id)
                action = "left" if success else "failed to leave"
                emoji = "❌" if success else "❌"
            
            if success:
                await interaction.response.send_message(f"{emoji} You have {action} the event '{event.name}'.", ephemeral=True)
            else:
                if join:
                    await interaction.response.send_message("❌ Failed to join event. You might already be in it or it's full.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Failed to leave event. You might not be in it.", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle slash event participation: {e}")
            await interaction.response.send_message("❌ An error occurred while processing your request.", ephemeral=True)

    @app_commands.command(name="clear-events", description="Effacer tous les événements de ce serveur")
    async def slash_clear_events(self, interaction: discord.Interaction):
        """Clear all events using slash commands"""
        try:
            
            # Get events for this guild
            guild_events = [event for event in self.event_service._events.values() 
                          if event.guild_id == interaction.guild_id]
            
            if not guild_events:
                await interaction.response.send_message("❌ No events found in this server.", ephemeral=True)
                return
            
            # Clear events
            cleared_count = 0
            for event in guild_events:
                if self.event_service.delete_event(event.event_id):
                    cleared_count += 1
            
            embed = discord.Embed(
                title="🧹 Events Cleared",
                description=f"Successfully cleared {cleared_count} event(s) from this server.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"User {interaction.user.id} cleared {cleared_count} events from guild {interaction.guild_id}")
                
        except Exception as e:
            logger.error(f"Failed to clear events via slash command: {e}")
            await interaction.response.send_message("❌ An error occurred while clearing events.", ephemeral=True)
    
    @app_commands.command(name="activer-pointage", description="Activer le système de pointage pour un événement")
    @app_commands.describe(
        event_id="ID de l'événement",
        duree_minutes="Durée du pointage en minutes (optionnel, par défaut : illimité)"
    )
    async def enable_checkin(self, interaction: discord.Interaction, event_id: str, duree_minutes: int = 0):
        """Activer le système de pointage pour un événement"""
        try:
            event = self.event_service.get_event(event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé",
                    ephemeral=True
                )
                return
            
            # Check permissions - only creator or admin can enable check-in
            user_is_admin = False
            try:
                if hasattr(interaction.user, 'guild_permissions'):
                    user_is_admin = interaction.user.guild_permissions.administrator
            except:
                user_is_admin = False
            
            if event.creator_id != interaction.user.id and not user_is_admin:
                await interaction.response.send_message(
                    "❌ Vous n'avez pas l'autorisation de gérer cet événement",
                    ephemeral=True
                )
                return
            
            # Calculate end time if duration is provided
            end_time = None
            if duree_minutes and duree_minutes > 0:
                from datetime import datetime, timedelta
                end_time = datetime.utcnow() + timedelta(minutes=duree_minutes)
            
            success = self.event_service.enable_check_in(event_id, end_time=end_time)
            
            if success:
                duration_text = f" (durée: {duree_minutes} minutes)" if duree_minutes else " (durée illimitée)"
                await interaction.response.send_message(
                    f"✅ Pointage activé pour l'événement **{event.name}**{duration_text}\n"
                    f"Les participants peuvent maintenant se pointer avec `/pointer {event_id}`",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Impossible d'activer le pointage",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error in enable_checkin command: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors de l'activation du pointage",
                ephemeral=True
            )
    
    @app_commands.command(name="desactiver-pointage", description="Désactiver le système de pointage pour un événement")
    @app_commands.describe(event_id="ID de l'événement")
    async def disable_checkin(self, interaction: discord.Interaction, event_id: str):
        """Désactiver le système de pointage pour un événement"""
        try:
            event = self.event_service.get_event(event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé",
                    ephemeral=True
                )
                return
            
            # Check permissions - only creator or admin can disable check-in
            user_is_admin = False
            try:
                if hasattr(interaction.user, 'guild_permissions'):
                    user_is_admin = interaction.user.guild_permissions.administrator
            except:
                user_is_admin = False
            
            if event.creator_id != interaction.user.id and not user_is_admin:
                await interaction.response.send_message(
                    "❌ Vous n'avez pas l'autorisation de gérer cet événement",
                    ephemeral=True
                )
                return
            
            success = self.event_service.disable_check_in(event_id)
            
            if success:
                await interaction.response.send_message(
                    f"✅ Pointage désactivé pour l'événement **{event.name}**",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Impossible de désactiver le pointage",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error in disable_checkin command: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors de la désactivation du pointage",
                ephemeral=True
            )
    
    @app_commands.command(name="pointer", description="Se pointer à un événement")
    @app_commands.describe(event_id="ID de l'événement")
    async def checkin(self, interaction: discord.Interaction, event_id: str):
        """Se pointer à un événement"""
        try:
            event = self.event_service.get_event(event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé",
                    ephemeral=True
                )
                return
            
            # Check if user is a participant
            if not event.is_participant(interaction.user.id):
                await interaction.response.send_message(
                    "❌ Vous devez être inscrit à cet événement pour vous pointer",
                    ephemeral=True
                )
                return
            
            # Check if already checked in
            if event.is_checked_in(interaction.user.id):
                await interaction.response.send_message(
                    "❌ Vous êtes déjà pointé pour cet événement",
                    ephemeral=True
                )
                return
            
            # Check if check-in is enabled and active
            if not event.is_check_in_active():
                if not event.check_in_enabled:
                    await interaction.response.send_message(
                        "❌ Le pointage n'est pas activé pour cet événement",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ La période de pointage n'est pas active",
                        ephemeral=True
                    )
                return
            
            success = self.event_service.check_in_participant(event_id, interaction.user.id)
            
            if success:
                await interaction.response.send_message(
                    f"✅ Vous êtes maintenant pointé pour l'événement **{event.name}**\n"
                    f"Participants pointés: {event.checked_in_count}/{event.participant_count}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Impossible de vous pointer",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error in checkin command: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors du pointage",
                ephemeral=True
            )
    
    @app_commands.command(name="rapport-presence", description="Afficher le rapport de présence d'un événement")
    @app_commands.describe(event_id="ID de l'événement")
    async def attendance_report(self, interaction: discord.Interaction, event_id: str):
        """Afficher le rapport de présence d'un événement"""
        try:
            event = self.event_service.get_event(event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé",
                    ephemeral=True
                )
                return
            
            # Check permissions - only creator or admin can view attendance report
            user_is_admin = False
            try:
                if hasattr(interaction.user, 'guild_permissions'):
                    user_is_admin = interaction.user.guild_permissions.administrator
            except:
                user_is_admin = False
            
            if event.creator_id != interaction.user.id and not user_is_admin:
                await interaction.response.send_message(
                    "❌ Vous n'avez pas l'autorisation de voir ce rapport",
                    ephemeral=True
                )
                return
            
            report = self.event_service.get_attendance_report(event_id)
            if not report:
                await interaction.response.send_message(
                    "❌ Impossible de générer le rapport de présence",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"📊 Rapport de présence",
                description=f"**{report['event_name']}** (ID: {event_id})",
                color=0x00ff00 if report['attendance_rate'] >= 70 else 0xff9900 if report['attendance_rate'] >= 50 else 0xff0000
            )
            
            # Statistics
            embed.add_field(
                name="📈 Statistiques",
                value=(
                    f"**Inscrits:** {report['total_participants']}\n"
                    f"**Pointés:** {report['checked_in_count']}\n"
                    f"**Taux de présence:** {report['attendance_rate']:.1f}%\n"
                    f"**Pointage actif:** {'Oui' if report['check_in_active'] else 'Non'}"
                ),
                inline=True
            )
            
            # Present participants
            if report['checked_in_participants']:
                present_users = []
                for user_id in report['checked_in_participants'][:10]:  # Limit to first 10
                    if interaction.guild:
                        user = interaction.guild.get_member(user_id)
                        present_users.append(user.display_name if user else f"Utilisateur {user_id}")
                    else:
                        present_users.append(f"Utilisateur {user_id}")
                
                present_text = "\n".join(present_users)
                if len(report['checked_in_participants']) > 10:
                    present_text += f"\n... et {len(report['checked_in_participants']) - 10} autres"
                
                embed.add_field(
                    name="✅ Participants présents",
                    value=present_text or "Aucun",
                    inline=True
                )
            
            # Absent participants
            if report['no_show_participants']:
                absent_users = []
                for user_id in report['no_show_participants'][:10]:  # Limit to first 10
                    if interaction.guild:
                        user = interaction.guild.get_member(user_id)
                        absent_users.append(user.display_name if user else f"Utilisateur {user_id}")
                    else:
                        absent_users.append(f"Utilisateur {user_id}")
                
                absent_text = "\n".join(absent_users)
                if len(report['no_show_participants']) > 10:
                    absent_text += f"\n... et {len(report['no_show_participants']) - 10} autres"
                
                embed.add_field(
                    name="❌ Participants absents",
                    value=absent_text or "Aucun",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in attendance_report command: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors de la génération du rapport",
                ephemeral=True
            )
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle reactions for joining/leaving events"""
        if user.bot:
            return
        
        try:
            # Find event by message ID
            event = self.event_service.get_event_by_message_id(reaction.message.id)
            
            if not event:
                return
            
            if reaction.emoji == "🎮":
                # Participer à l'événement
                success = self.event_service.add_participant(event.event_id, user.id)
                if success:
                    # Update the embed
                    embed = EventEmbeds.create_event_embed(event, self.bot)
                    await reaction.message.edit(embed=embed)
            
            elif reaction.emoji == "🚪":
                # Ne plus participer à l'événement
                success = self.event_service.remove_participant(event.event_id, user.id)
                if success:
                    # Update the embed
                    embed = EventEmbeds.create_event_embed(event, self.bot)
                    await reaction.message.edit(embed=embed)
        
        except Exception as e:
            logger.error(f"Failed to handle reaction: {e}")
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """Handle reaction removal (optional - for consistency)"""
        # We don't need to do anything special when reactions are removed
        # as the primary interaction is adding reactions
        pass
