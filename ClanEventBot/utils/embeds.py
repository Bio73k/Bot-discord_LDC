"""
Discord embed utilities for Destiny 2 bot
"""

import discord
from datetime import datetime
from typing import List
from models.event import Event
from utils.constants import EventType

class EventEmbeds:
    """Utility class for creating Discord embeds for events"""
    
    @staticmethod
    def get_user_display_name(bot, user_id: int) -> str:
        """Get a user's display name or fallback to mention"""
        if bot:
            user = bot.get_user(user_id)
            if user:
                return user.display_name
        return f"<@{user_id}>"
    
    EVENT_TYPE_COLORS = {
        EventType.BINGO: 0xff6b6b,      # Red
        EventType.PVP_TOURNAMENT: 0x4ecdc4,  # Teal
        EventType.GENERAL: 0x95e1d3     # Light green
    }
    
    EVENT_TYPE_EMOJIS = {
        EventType.BINGO: "🎯",
        EventType.PVP_TOURNAMENT: "⚔️",
        EventType.GENERAL: "📅"
    }
    
    @classmethod
    def create_event_embed(cls, event: Event, bot=None) -> discord.Embed:
        """Create an embed for displaying an event"""
        color = cls.EVENT_TYPE_COLORS.get(event.event_type, 0x00bfff)
        emoji = cls.EVENT_TYPE_EMOJIS.get(event.event_type, "📅")
        
        # Use event date/time as description if available, otherwise fall back to description
        description_text = ""
        if event.event_date:
            from utils.timezone_utils import format_french_datetime
            date_str = format_french_datetime(event.event_date)
            description_text = f"📅 **{date_str}**"
        elif event.description:
            description_text = event.description
        else:
            description_text = "Aucune description fournie"
            
        embed = discord.Embed(
            title=f"{emoji} {event.name}",
            description=description_text,
            color=color
        )
        
        # Show event type and team size
        event_details = f"**Type :** {event.event_type.value}"
        if event.team_size:
            if event.team_size == 1:
                event_details += f"\n**Format :** Solo (1 joueur)"
            else:
                event_details += f"\n**Format :** Équipes de {event.team_size} joueurs"
        
        embed.add_field(
            name="Détails de l'événement",
            value=event_details,
            inline=True
        )
        
        # Show participant list (mentions only, no count)
        if event.participants:
            participant_mentions = []
            for user_id in event.participants[:10]:  # Limit to first 10 to avoid embed limits
                participant_mentions.append(f"<@{user_id}>")
            
            if participant_mentions:
                participants_display = ", ".join(participant_mentions)
                if len(event.participants) > 10:
                    remaining = len(event.participants) - 10
                    participants_display += f" (+{remaining} autres)"
                
                embed.add_field(
                    name="Participants",
                    value=participants_display,
                    inline=False
                )
        else:
            embed.add_field(
                name="Participants",
                value="Aucun participant inscrit",
                inline=False
            )
        
        # Check-in information if enabled
        if event.check_in_enabled:
            check_in_status = "🟢 Actif" if event.is_check_in_active() else "🟡 Inactif"
            check_in_text = f"**Statut:** {check_in_status}\n"
            check_in_text += f"**Pointés:** {event.checked_in_count}/{event.participant_count}"
            
            if event.checked_in_count > 0:
                attendance_rate = (event.checked_in_count / event.participant_count) * 100
                check_in_text += f" ({attendance_rate:.0f}%)"
            
            embed.add_field(
                name="📋 Pointage",
                value=check_in_text,
                inline=True
            )
        
        # Team information if teams exist - show detailed team assignments
        if event.has_teams:
            teams_text = f"**{event.team_count} équipes de {event.team_size} joueurs**\n\n"
            
            for i, team in enumerate(event.teams, 1):
                team_members = [f"<@{user_id}>" for user_id in team]
                teams_text += f"**Équipe {i}:** {', '.join(team_members)}\n"
            
            # Show unassigned players if any
            assigned_players = set()
            for team in event.teams:
                assigned_players.update(team)
            unassigned = [user_id for user_id in event.participants if user_id not in assigned_players]
            
            if unassigned:
                unassigned_mentions = [f"<@{user_id}>" for user_id in unassigned]
                teams_text += f"\n**Non assignés:** {', '.join(unassigned_mentions)}"
            
            embed.add_field(
                name="⚔️ Équipes",
                value=teams_text,
                inline=False
            )
        

        

        
        return embed
    
    @classmethod
    def create_events_list_embed(cls, events: List[Event]) -> discord.Embed:
        """Create an embed listing multiple events"""
        embed = discord.Embed(
            title="📅 Événements actifs",
            description=f"Trouvé {len(events)} événement(s) actif(s)",
            color=0x00bfff
        )
        
        for event in events[:10]:  # Limit to first 10 events
            emoji = cls.EVENT_TYPE_EMOJIS.get(event.event_type, "📅")
            
            # Create event summary
            participants_info = f"{event.participant_count}/{event.max_participants}"
            if event.is_full:
                participants_info += " (COMPLET)"
            
            teams_info = ""
            if event.has_teams:
                teams_info = f" | {event.team_count} équipes"
            
            value = (
                f"**Type :** {event.event_type.value}\n"
                f"**Participants :** {participants_info}{teams_info}\n"
                f"**ID :** `{event.event_id}`"
            )
            
            embed.add_field(
                name=f"{emoji} {event.name}",
                value=value,
                inline=True
            )
        
        if len(events) > 10:
            embed.add_field(
                name="⚠️ Note",
                value=f"Showing first 10 of {len(events)} events. Use `!event-info <id>` for details.",
                inline=False
            )
        
        embed.set_footer(text="Use !event-info <id> to see detailed information about an event")
        
        return embed
    
    @classmethod
    def create_event_detail_embed(cls, event: Event, bot=None) -> discord.Embed:
        """Create a detailed embed for a specific event"""
        color = cls.EVENT_TYPE_COLORS.get(event.event_type, 0x00bfff)
        emoji = cls.EVENT_TYPE_EMOJIS.get(event.event_type, "📅")
        
        embed = discord.Embed(
            title=f"{emoji} {event.name} - Detailed View",
            description=event.description or "No description provided",
            color=color,
            timestamp=event.created_at
        )
        
        # Basic information
        embed.add_field(
            name="📊 Event Information",
            value=(
                f"**Type:** {event.event_type.value}\n"
                f"**Status:** {event.status.value}\n"
                f"**Event ID:** `{event.event_id}`\n"
                f"**Created:** {event.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
            ),
            inline=False
        )
        
        # Participant details
        participant_info = (
            f"**Count:** {event.participant_count}/{event.max_participants}\n"
            f"**Available Spots:** {event.max_participants - event.participant_count}"
        )
        
        if event.is_full:
            participant_info += "\n**Status:** ⚠️ Event is FULL"
        
        embed.add_field(
            name="👥 Participants",
            value=participant_info,
            inline=True
        )
        
        # Check-in information
        if event.check_in_enabled:
            check_in_status = "🟢 Active" if event.is_check_in_active() else "🟡 Inactive"
            check_in_info = (
                f"**Status:** {check_in_status}\n"
                f"**Checked In:** {event.checked_in_count}/{event.participant_count}\n"
                f"**Attendance Rate:** {event.attendance_rate:.1f}%"
            )
            
            embed.add_field(
                name="📋 Check-in",
                value=check_in_info,
                inline=True
            )
        
        # Team information
        if event.has_teams:
            team_info = (
                f"**Teams:** {event.team_count}\n"
                f"**Team Size:** {event.team_size}\n"
                f"**Players in Teams:** {sum(len(team) for team in event.teams)}"
            )
            
            embed.add_field(
                name="⚔️ Teams",
                value=team_info,
                inline=True
            )
        else:
            embed.add_field(
                name="⚔️ Teams",
                value="No teams assigned yet",
                inline=True
            )
        

        
        # Show participant list if there are participants
        if event.participants and bot:
            participant_names = []
            for user_id in event.participants[:20]:  # Limit to first 20 to avoid embed limits
                participant_names.append(cls.get_user_display_name(bot, user_id))
            
            if participant_names:
                participants_text = "\n".join(participant_names)
                if len(event.participants) > 20:
                    participants_text += f"\n... and {len(event.participants) - 20} more"
                
                embed.add_field(
                    name="👥 Liste des participants",
                    value=participants_text,
                    inline=False
                )
        

        
        return embed

class TeamEmbeds:
    """Utility class for creating Discord embeds for teams"""
    
    @classmethod
    def create_teams_embed(cls, event: Event, teams: List[List[int]], bot=None) -> discord.Embed:
        """Create an embed displaying team assignments"""
        emoji = EventEmbeds.EVENT_TYPE_EMOJIS.get(event.event_type, "📅")
        color = EventEmbeds.EVENT_TYPE_COLORS.get(event.event_type, 0x00bfff)
        
        embed = discord.Embed(
            title=f"{emoji} {event.name} - Team Assignments",
            description=f"Teams for {event.event_type.value} event",
            color=color
        )
        
        if not teams:
            embed.add_field(
                name="⚠️ No Teams",
                value="No teams have been created yet.",
                inline=False
            )
            return embed
        
        # Team statistics
        total_players_in_teams = sum(len(team) for team in teams)
        unassigned_players = event.participant_count - total_players_in_teams
        
        embed.add_field(
            name="📊 Team Statistics",
            value=(
                f"**Total Teams:** {len(teams)}\n"
                f"**Team Size:** {event.team_size}\n"
                f"**Players in Teams:** {total_players_in_teams}\n"
                f"**Unassigned Players:** {unassigned_players}"
            ),
            inline=False
        )
        
        # Display each team
        team_emojis = ["🔵", "🔴", "🟡", "🟢", "🟠", "🟣", "⚫", "⚪"]
        
        for i, team in enumerate(teams):
            team_number = i + 1
            emoji_index = i % len(team_emojis)
            team_emoji = team_emojis[emoji_index]
            
            # Format team members (try to get usernames, fall back to mentions)
            team_members = []
            for user_id in team:
                if bot:
                    user = bot.get_user(user_id)
                    if user:
                        team_members.append(f"{user.display_name}")
                    else:
                        team_members.append(f"<@{user_id}>")
                else:
                    team_members.append(f"<@{user_id}>")
            
            embed.add_field(
                name=f"{team_emoji} Team {team_number}",
                value="\n".join(team_members) if team_members else "No members",
                inline=True
            )
        
        # Add warning if there are unassigned players
        if unassigned_players > 0:
            embed.add_field(
                name="⚠️ Unassigned Players",
                value=(
                    f"{unassigned_players} player(s) could not be assigned to teams "
                    f"due to team size constraints."
                ),
                inline=False
            )
        
        embed.set_footer(text=f"Teams created for event: {event.event_id}")
        
        return embed
    
    @classmethod
    def create_team_summary_embed(cls, event: Event) -> discord.Embed:
        """Create a summary embed for team information"""
        emoji = EventEmbeds.EVENT_TYPE_EMOJIS.get(event.event_type, "📅")
        color = EventEmbeds.EVENT_TYPE_COLORS.get(event.event_type, 0x00bfff)
        
        embed = discord.Embed(
            title=f"{emoji} {event.name} - Team Summary",
            color=color
        )
        
        if not event.has_teams:
            embed.description = "No teams have been created for this event yet."
            embed.add_field(
                name="Create Teams",
                value=f"Use `!randomize-teams {event.event_id} <size>` to create teams",
                inline=False
            )
        else:
            total_in_teams = sum(len(team) for team in event.teams)
            embed.description = f"Team assignments for {event.event_type.value} event"
            
            embed.add_field(
                name="Team Information",
                value=(
                    f"**Total Teams:** {event.team_count}\n"
                    f"**Team Size:** {event.team_size}\n"
                    f"**Players in Teams:** {total_in_teams}/{event.participant_count}"
                ),
                inline=False
            )
        
        return embed

class GeneralEmbeds:
    """General utility embeds"""
    
    @classmethod
    def create_error_embed(cls, message: str) -> discord.Embed:
        """Create an error embed"""
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=0xff0000
        )
        return embed
    
    @classmethod
    def create_success_embed(cls, title: str, message: str) -> discord.Embed:
        """Create a success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=message,
            color=0x00ff00
        )
        return embed
    
    @classmethod
    def create_info_embed(cls, title: str, message: str) -> discord.Embed:
        """Create an info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=message,
            color=0x00bfff
        )
        return embed
