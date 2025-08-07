"""
Event interaction buttons using Discord UI components
"""

import discord
import logging
from services.event_service import EventService
from utils.embeds import EventEmbeds

logger = logging.getLogger(__name__)

class EventParticipationView(discord.ui.View):
    """View with buttons for event participation"""
    
    def __init__(self, event_id: str, event_service: EventService, bot=None):
        super().__init__(timeout=None)  # Persistent view
        self.event_id = event_id
        self.event_service = event_service
        self.bot = bot
    
    @discord.ui.button(label="🎮 Participer", style=discord.ButtonStyle.green, custom_id="join_event")
    async def join_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle join event button click"""
        try:
            event = self.event_service.get_event(self.event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé", ephemeral=True
                )
                return
            
            success = self.event_service.add_participant(self.event_id, interaction.user.id)
            
            if success:
                # Update the embed
                embed = EventEmbeds.create_event_embed(event, self.bot)
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                if event.is_participant(interaction.user.id):
                    await interaction.response.send_message(
                        "✅ Vous participez déjà à cet événement", ephemeral=True
                    )
                elif event.is_full:
                    await interaction.response.send_message(
                        "❌ L'événement est complet", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Impossible de rejoindre l'événement", ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in join_event button: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite", ephemeral=True
            )
    
    @discord.ui.button(label="🚪 Ne plus participer", style=discord.ButtonStyle.red, custom_id="leave_event")
    async def leave_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle leave event button click"""
        try:
            event = self.event_service.get_event(self.event_id)
            if not event:
                await interaction.response.send_message(
                    "❌ Événement non trouvé", ephemeral=True
                )
                return
            
            success = self.event_service.remove_participant(self.event_id, interaction.user.id)
            
            if success:
                # Update the embed
                embed = EventEmbeds.create_event_embed(event, self.bot)
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message(
                    "❌ Vous ne participez pas à cet événement", ephemeral=True
                )
        
        except Exception as e:
            logger.error(f"Error in leave_event button: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite", ephemeral=True
            )