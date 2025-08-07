"""
Interactive event creation modal and views for Discord
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from typing import Optional
from utils.constants import EventType, EVENT_TYPE_INFO, VALID_TEAM_SIZES

logger = logging.getLogger(__name__)

class EventTypeSelectView(discord.ui.View):
    """View for selecting event type with dropdown"""
    
    def __init__(self, user_id: int, timeout: float = 300.0):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.selected_type: Optional[EventType] = None
        
        # Add the select dropdown
        self.type_select = EventTypeSelect()
        self.add_item(self.type_select)
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Vous ne pouvez pas utiliser cette interface.",
                ephemeral=True
            )
            return False
        return True

class EventTypeSelect(discord.ui.Select):
    """Dropdown for selecting event type"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Bingo",
                description="Défis Destiny 2 en format bingo",
                emoji="🎲",
                value="Bingo"
            ),
            discord.SelectOption(
                label="Tournoi JcJ",
                description="Tournoi compétitif en JcJ",
                emoji="⚔️",
                value="Tournoi JcJ"
            ),
            discord.SelectOption(
                label="Événement général",
                description="Activité générale du clan",
                emoji="🎮",
                value="Événement général"
            )
        ]
        
        super().__init__(
            placeholder="🎯 Choisissez le type d'événement...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle event type selection"""
        try:
            # Get selected event type value
            event_type_value = self.values[0]
            
            # Find the corresponding EventType
            event_type = None
            for et in EventType:
                if et.value == event_type_value:
                    event_type = et
                    break
            
            if not event_type:
                raise ValueError(f"Unknown event type: {event_type_value}")
            
            # Store selection in view
            if self.view:
                self.view.selected_type = event_type
            
            # Create and show the details modal directly
            modal = EventDetailsModal(event_type)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"Error in event type selection: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Une erreur s'est produite lors de la sélection du type.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Une erreur s'est produite lors de la sélection du type.",
                        ephemeral=True
                    )
            except Exception as follow_error:
                logger.error(f"Failed to send error message: {follow_error}")


class EventDetailsModal(discord.ui.Modal):
    """Modal for entering event details"""
    
    def __init__(self, event_type: EventType):
        super().__init__(
            title=f"Créer un {event_type.value}",
            timeout=600.0  # 10 minutes
        )
        self.event_type = event_type
        
        # Event name input
        self.name_input = discord.ui.TextInput(
            label="Nom de l'événement",
            placeholder="Ex: Raid du Jardin du Salut",
            min_length=1,
            max_length=100,
            required=True
        )
        self.add_item(self.name_input)
        
        # Date input
        self.date_input = discord.ui.TextInput(
            label="Date (JJ/MM/AAAA)",
            placeholder="Ex: 25/12/2024",
            min_length=10,
            max_length=10,
            required=True
        )
        self.add_item(self.date_input)
        
        # Time input
        self.time_input = discord.ui.TextInput(
            label="Heure (HH:MM)",
            placeholder="Ex: 20:30",
            min_length=5,
            max_length=5,
            required=True
        )
        self.add_item(self.time_input)
        
        # Team size input
        self.team_size_input = discord.ui.TextInput(
            label="Taille d'équipe (1-6 joueurs)",
            placeholder="Ex: 3 pour des équipes de 3 joueurs",
            min_length=1,
            max_length=1,
            required=True
        )
        self.add_item(self.team_size_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission"""
        try:
            # Get form values
            name = self.name_input.value.strip()
            description = f"Événement {self.event_type.value} organisé par le clan"
            date_str = self.date_input.value.strip()
            time_str = self.time_input.value.strip()
            team_size_str = self.team_size_input.value.strip()
            
            # Parse and validate team size
            try:
                team_size = int(team_size_str)
                if team_size < 1 or team_size > 6:
                    await interaction.response.send_message(
                        "❌ La taille d'équipe doit être entre 1 et 6 joueurs.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ La taille d'équipe doit être un nombre valide entre 1 et 6.",
                    ephemeral=True
                )
                return
            
            # Parse and validate date
            try:
                day, month, year = map(int, date_str.split('/'))
                if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2024):
                    raise ValueError("Date invalide")
            except (ValueError, IndexError):
                await interaction.response.send_message(
                    "❌ Format de date invalide. Utilisez JJ/MM/AAAA (ex: 25/12/2024)",
                    ephemeral=True
                )
                return
            
            # Parse and validate time
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Heure invalide")
            except (ValueError, IndexError):
                await interaction.response.send_message(
                    "❌ Format d'heure invalide. Utilisez HH:MM (ex: 20:30)",
                    ephemeral=True
                )
                return
            
            # Create datetime object using French timezone
            try:
                from utils.timezone_utils import parse_french_datetime
                
                # Parse French time to UTC for storage
                event_datetime = parse_french_datetime(date_str, time_str)
                
                # Check if date is in the past (compare in UTC)
                if event_datetime <= datetime.utcnow():
                    await interaction.response.send_message(
                        "❌ La date et l'heure doivent être dans le futur (heure française).",
                        ephemeral=True
                    )
                    return
                    
            except ValueError as e:
                await interaction.response.send_message(
                    f"❌ {str(e)}",
                    ephemeral=True
                )
                return
            
            # Create the event using the bot's event service
            bot = interaction.client
            event_service = getattr(bot, 'event_service', None)
            
            if not event_service:
                await interaction.response.send_message(
                    "❌ Service d'événements non disponible.",
                    ephemeral=True
                )
                return
            
            # Create event
            event = event_service.create_event(
                event_type=self.event_type,
                name=name,
                description=description,
                creator_id=interaction.user.id,
                guild_id=interaction.guild_id,
                max_participants=100,  # Fixed at 100
                event_date=event_datetime,
                team_size=team_size
            )
            
            if not event:
                await interaction.response.send_message(
                    "❌ Erreur lors de la création de l'événement.",
                    ephemeral=True
                )
                return
            
            # Create event embed and buttons
            from utils.embeds import EventEmbeds
            from utils.event_buttons import EventParticipationView
            
            embed = EventEmbeds.create_event_embed(event, bot)
            view = EventParticipationView(event.event_id, event_service, bot)
            
            # Send event message with buttons
            message = await interaction.response.send_message(embed=embed, view=view)
            
            # Get the message object for storing ID
            original_message = await interaction.original_response()
            event.message_id = original_message.id
            
            # Link message to event in service for reaction handling
            event_service.link_message_to_event(original_message.id, event.event_id)
            
            # Create thread for discussion
            try:
                thread = await original_message.create_thread(
                    name=f"🧵 {name}",
                    auto_archive_duration=4320,  # 3 days
                    reason="Thread de discussion pour l'événement"
                )
                
                # Store thread ID
                event.thread_id = thread.id
                
                # Send welcome message in thread with role ping
                from utils.timezone_utils import format_french_datetime
                french_time = format_french_datetime(event_datetime)
                
                welcome_message = (
                    f"🎮 **Bienvenue dans le thread de l'événement !**\n\n"
                    f"📋 **{name}**\n"
                    f"📅 **{french_time}** (heure française)\n\n"
                    f"<@&1348280452305260554> Un nouvel événement vous attend !\n\n"
                    f"Utilisez ce fil pour discuter, poser des questions et vous coordonner !"
                )
                
                await thread.send(welcome_message)
                
                logger.info(f"Created thread {thread.id} for event {event.event_id}")
                
            except Exception as e:
                logger.error(f"Failed to create thread for event {event.event_id}: {e}")
            
            logger.info(f"Created {self.event_type.value} event via interactive modal: {name} (ID: {event.event_id})")
            
        except Exception as e:
            logger.error(f"Error creating event via modal: {e}")
            try:
                await interaction.response.send_message(
                    "❌ Une erreur s'est produite lors de la création de l'événement.",
                    ephemeral=True
                )
            except:
                # If response already sent, use followup
                await interaction.followup.send(
                    "❌ Une erreur s'est produite lors de la création de l'événement.",
                    ephemeral=True
                )
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """Handle modal errors"""
        logger.error(f"Modal error: {error}")
        try:
            await interaction.response.send_message(
                "❌ Une erreur s'est produite. Veuillez réessayer.",
                ephemeral=True
            )
        except:
            await interaction.followup.send(
                "❌ Une erreur s'est produite. Veuillez réessayer.",
                ephemeral=True
            )