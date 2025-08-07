"""
Discord View for team size selection
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TeamSizeSelectionView(discord.ui.View):
    """Interactive view for selecting team size before automatic team creation"""
    
    def __init__(self, event, bot, timeout: float = 300.0):
        super().__init__(timeout=timeout)
        self.event = event
        self.bot = bot
        self.selected_size: Optional[int] = None
        self.responded = False
        self.message: Optional[discord.Message] = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the event creator to interact"""
        if interaction.user.id != self.event.creator_id:
            await interaction.response.send_message(
                "❌ Seul l'organisateur de l'événement peut choisir la taille des équipes.",
                ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self) -> None:
        """Called when the view times out"""
        logger.warning(f"Team size selection timed out for event {self.event.event_id}")
        
        # Disable all buttons
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        
        # Try to edit the original message if possible
        try:
            if hasattr(self, 'message') and self.message:
                embed = discord.Embed(
                    title="⏰ Temps écoulé",
                    description=f"La sélection de taille d'équipes pour '{self.event.name}' a expiré.\nUtilisez `/randomize-teams` manuellement si nécessaire.",
                    color=0xffaa00
                )
                await self.message.edit(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Failed to update timeout message: {e}")
    
    @discord.ui.button(label="1 joueur (Solo)", style=discord.ButtonStyle.secondary, emoji="🎯")
    async def team_size_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_team_size_selection(interaction, 1)
    
    @discord.ui.button(label="2 joueurs", style=discord.ButtonStyle.secondary, emoji="👥")
    async def team_size_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_team_size_selection(interaction, 2)
    
    @discord.ui.button(label="3 joueurs", style=discord.ButtonStyle.secondary, emoji="🔺")
    async def team_size_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_team_size_selection(interaction, 3)
    
    @discord.ui.button(label="4 joueurs", style=discord.ButtonStyle.secondary, emoji="🔷")
    async def team_size_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_team_size_selection(interaction, 4)
    
    @discord.ui.button(label="6 joueurs", style=discord.ButtonStyle.primary, emoji="⭐")
    async def team_size_6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_team_size_selection(interaction, 6)
    
    @discord.ui.button(label="Pas d'équipes", style=discord.ButtonStyle.danger, emoji="❌")
    async def no_teams(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Skip team creation"""
        self.responded = True
        self.selected_size = None
        
        # Disable all buttons
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        
        embed = discord.Embed(
            title="❌ Création d'équipes annulée",
            description=f"Aucune équipe ne sera créée pour '{self.event.name}'.\nVous pouvez toujours utiliser `/randomize-teams` plus tard.",
            color=0xff4444
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def _handle_team_size_selection(self, interaction: discord.Interaction, team_size: int):
        """Handle team size selection and create teams"""
        self.responded = True
        self.selected_size = team_size
        
        # Disable all buttons
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        
        # Check if there are enough participants
        if not self.event.participants:
            embed = discord.Embed(
                title="❌ Aucun participant",
                description=f"Impossible de créer des équipes car il n'y a aucun participant pour '{self.event.name}'.",
                color=0xff4444
            )
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()
            return
        
        try:
            # Create teams using the team service
            team_service = self.bot.team_service
            teams = team_service.randomize_teams(self.event.participants, team_size)
            
            if not teams:
                embed = discord.Embed(
                    title="❌ Échec de création",
                    description=f"Impossible de créer des équipes de {team_size} joueur(s).\nPas assez de participants.",
                    color=0xff4444
                )
                await interaction.response.edit_message(embed=embed, view=self)
                self.stop()
                return
            
            # Update event with teams
            self.event.teams = teams
            self.event.team_size = team_size
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Équipes créées automatiquement !",
                description=f"**{len(teams)} équipes** de **{team_size} joueur(s)** créées pour '{self.event.name}'.\n\nConsultez le fil pour voir les compositions !",
                color=0x00ff00
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
            # Post detailed teams in thread
            if self.event.thread_id:
                try:
                    thread = self.bot.get_channel(self.event.thread_id)
                    if not thread:
                        thread = await self.bot.fetch_channel(self.event.thread_id)
                    
                    if thread:
                        from utils.embeds import TeamEmbeds
                        teams_embed = TeamEmbeds.create_teams_embed(self.event, teams, self.bot)
                        await thread.send("⚔️ **Équipes créées automatiquement !**", embed=teams_embed)
                        
                except Exception as e:
                    logger.error(f"Failed to post teams in thread {self.event.thread_id}: {e}")
            
            logger.info(f"Auto-created {len(teams)} teams of size {team_size} for event {self.event.event_id}")
            
        except Exception as e:
            logger.error(f"Failed to create teams automatically: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur s'est produite lors de la création des équipes.\nUtilisez `/randomize-teams` manuellement.",
                color=0xff4444
            )
            await interaction.response.edit_message(embed=embed, view=self)
        
        self.stop()