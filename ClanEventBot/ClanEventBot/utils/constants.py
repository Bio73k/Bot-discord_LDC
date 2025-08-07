"""
Constants for the Destiny 2 Discord bot
"""

from enum import Enum

class EventType(Enum):
    """Types of events that can be created"""
    BINGO = "Bingo"
    PVP_TOURNAMENT = "Tournoi JcJ"
    GENERAL = "Événement général"

class EventStatus(Enum):
    """Status of events"""
    OPEN = "Ouvert"
    FULL = "Complet"
    IN_PROGRESS = "En cours"
    COMPLETED = "Terminé"
    CANCELLED = "Annulé"

# Team size constraints
VALID_TEAM_SIZES = [1, 2, 3, 4, 6]

# Event constraints
MAX_PARTICIPANTS_PER_EVENT = 100
MIN_PARTICIPANTS_FOR_TEAMS = 2

# Discord limits
EMBED_FIELD_VALUE_LIMIT = 1024
EMBED_DESCRIPTION_LIMIT = 4096
MAX_EMBED_FIELDS = 25

# Event type descriptions and suggested team sizes
EVENT_TYPE_INFO = {
    EventType.BINGO: {
        "description": "Défis Bingo avec divers objectifs à accomplir",
        "suggested_team_sizes": [2, 3],
        "max_participants": 100
    },
    EventType.PVP_TOURNAMENT: {
        "description": "Competitive PvP tournament brackets",
        "suggested_team_sizes": [2, 3, 4, 6],
        "max_participants": 100
    },
    EventType.GENERAL: {
        "description": "General clan activities and events",
        "suggested_team_sizes": [2, 3, 4, 6],
        "max_participants": 100
    }
}

# Bot configuration
BOT_PREFIX = "!"
BOT_DESCRIPTION = "Destiny 2 Clan Event Management Bot"

# Command cooldowns (in seconds)
COMMAND_COOLDOWNS = {
    "create_event": 30,
    "randomize_teams": 10,
    "join_event": 5,
    "leave_event": 5
}

# Reaction emojis for events
REACTION_JOIN = "🎮"  # Gaming controller for "Participer"
REACTION_LEAVE = "🚪"  # Door for "Ne plus participer"

# Color scheme for embeds
COLORS = {
    "primary": 0x00bfff,    # Light blue
    "success": 0x00ff00,    # Green
    "error": 0xff0000,      # Red
    "warning": 0xffff00,    # Yellow
    "info": 0x888888        # Gray
}

# Team emoji mapping for visual representation
TEAM_EMOJIS = [
    "🔵", "🔴", "🟡", "🟢", "🟠", "🟣", 
    "⚫", "⚪", "🟤", "🔷", "🔶", "💎"
]

# Event creation templates
EVENT_TEMPLATES = {
    EventType.BINGO: {
        "default_description": "Complete various Destiny 2 challenges in a bingo format!",
        "instructions": "React with ✅ to join the bingo event. Teams will be randomized before the event starts."
    },
    EventType.PVP_TOURNAMENT: {
        "default_description": "Competitive PvP tournament with bracket progression!",
        "instructions": "React with ✅ to join the tournament. Teams will be created for the tournament format."
    },
    EventType.GENERAL: {
        "default_description": "General clan activity - let's play together!",
        "instructions": "React with ✅ to join this clan event. Team sizes will be determined based on the activity."
    }
}

# Help text sections
HELP_SECTIONS = {
    "events": {
        "title": "📅 Event Commands",
        "commands": [
            ("!create-bingo <name> <description>", "Create a Bingo event"),
            ("!create-pvp <name> <description>", "Create a PvP Tournament"),
            ("!create-general <name> <description>", "Create a General event"),
            ("!events", "List all active events"),
            ("!event-info <event_id>", "Show detailed event information"),
            ("!delete-event <event_id>", "Delete an event (creator/admin only)"),
            ("!join-event <event_id>", "Join an event"),
            ("!leave-event <event_id>", "Leave an event")
        ]
    },
    "teams": {
        "title": "⚔️ Team Commands",
        "commands": [
            ("!randomize-teams <event_id> <team_size>", "Create randomized teams"),
            ("!show-teams <event_id>", "Display current team assignments"),
            ("!clear-teams <event_id>", "Clear all team assignments"),
            ("!team-stats <event_id>", "Show team statistics")
        ]
    },
    "tips": {
        "title": "ℹ️ Tips & Info",
        "items": [
            "React with ✅ to join events quickly",
            "React with ❌ to leave events",
            "Events support up to 100 participants",
            "Valid team sizes: 1, 2, 3, 4, or 6 players",
            "Event creators and server admins can manage events",
            "Teams are randomized for fair gameplay"
        ]
    }
}

# Error messages
ERROR_MESSAGES = {
    "event_not_found": "❌ Event not found. Please check the event ID.",
    "event_full": "❌ This event is full and cannot accept more participants.",
    "already_participant": "❌ You are already a participant in this event.",
    "not_participant": "❌ You are not a participant in this event.",
    "insufficient_permissions": "❌ You don't have permission to perform this action.",
    "invalid_team_size": "❌ Team size must be 1, 2, 3, 4, or 6 players.",
    "no_participants": "❌ No participants available for team creation.",
    "teams_already_exist": "❌ Teams already exist for this event. Clear them first if you want to recreate.",
    "no_teams": "❌ No teams have been created for this event yet.",
    "command_cooldown": "❌ Please wait before using this command again."
}

# Success messages
SUCCESS_MESSAGES = {
    "event_created": "✅ Event created successfully! React with ✅ to join.",
    "joined_event": "✅ You have joined the event!",
    "left_event": "✅ You have left the event.",
    "teams_created": "✅ Teams have been randomized successfully!",
    "teams_cleared": "✅ All team assignments have been cleared.",
    "event_deleted": "✅ Event has been deleted successfully."
}
