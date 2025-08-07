# Overview

This is a Discord bot for Destiny 2 clan event management that helps organize clan activities, manage participants, and create team assignments. The bot supports multiple event types including Bingo challenges, PvP tournaments, raids, and general events. It provides commands for creating events, managing participants, and randomizing team assignments with appropriate team sizes for different Destiny 2 activities.

# User Preferences

Preferred communication style: Simple, everyday language.
Bot interface: Slash commands (/) preferred over prefix commands (!).
Event creation: Support for custom event types beyond predefined categories.
Command suggestions: Provide specific command suggestions rather than generic "use help" messages.
Event management: Clear events command available to all users (no admin restriction required).
Event threads: Automatic thread creation in the same channel where events are planned, with @Gardiens role pinging for notifications.
Language: Bot interface fully localized in French including slash commands, embeds, and messages.
Bingo events: Description updated to be game-agnostic (removed "Destiny" reference) making it applicable to any game with challenge objectives.
Event scheduling: Mandatory date and time parameters for all events with French date format (DD/MM/YYYY HH:MM). All times are handled in French timezone (UTC+2) - users input French time and all displays show French time, with UTC conversion handled internally.
Interface: Removed automatic timestamps and creator attribution from event displays for cleaner presentation. Replaced emoji reactions with Discord buttons featuring clear text ("🎮 Participer", "🚪 Ne plus participer") and removed "Comment rejoindre" instructions since buttons are self-explanatory.
Notifications: Automatic reminder system that pings all participants 2 minutes before event start time (for testing, normally 10 minutes).
Display: Event date/time now prominently displayed in the embed description instead of event description.
Storage: Events stored in memory (will reset on bot restart) - designed for easy database migration later.
Team size selection: Interactive event creation uses a 2-step process: first select event type (Bingo/Tournoi JcJ/Événement général) from dropdown, then fill event details form with 4 fields: name, date, time, and team size (1-6 players). Max participants fixed at 100, description auto-generated.
Check-in system: Comprehensive attendance tracking with /activer-pointage, /desactiver-pointage, /pointer, and /rapport-presence commands. Event creators and admins can enable/disable check-in periods, participants can check in when active, and detailed attendance reports show present/absent participants with statistics.

# System Architecture

## Application Structure
The project follows a modular architecture with clear separation of concerns:
- **Entry Point**: `main.py` serves as the application launcher with proper error handling and logging
- **Bot Core**: Discord.py-based bot implementation with command prefix `!` and necessary intents
- **Commands**: Organized into separate cogs for event management and team management
- **Services**: Business logic layer handling event operations and team assignment algorithms
- **Models**: Data models representing events and participants with in-memory storage
- **Utilities**: Helper modules for constants, Discord embeds, and formatting

## Discord Bot Framework
Uses discord.py with the commands extension for structured command handling. The bot implements:
- Command prefix system (`!` prefix)
- Cog-based command organization for modularity
- Proper Discord intents for message content and reactions
- Comprehensive logging throughout the application

## Event Management System
Events are represented with the following key features:
- Multiple event types (Bingo, PvP Tournament, Raid, General)
- Participant tracking with Discord user IDs
- Team assignment capabilities with configurable team sizes
- Event status management (Open, Full, In Progress, Completed, Cancelled)
- Message tracking for Discord integration
- Check-in system for attendance tracking with time-based controls
- Attendance rate calculation and detailed reporting
- No-show participant identification

## Team Assignment Algorithm
Implements a randomization service that:
- Validates team sizes against Destiny 2 activity requirements (2, 3, 4, or 6 players)
- Randomly shuffles participants before team assignment
- Handles remainder participants when total doesn't divide evenly into teams
- Provides error handling for insufficient participants

## Data Storage Strategy
Currently uses in-memory storage for MVP implementation:
- Dictionary-based storage for events and participants
- Message ID to event ID mapping for Discord integration
- Designed for easy migration to persistent database storage

## Permission and Security Model
Implements role-based access control:
- Event creators can manage their own events
- Server administrators have full management permissions
- Participant management restricted to authorized users
- Guild-specific event isolation

# External Dependencies

## Discord API
- **discord.py**: Primary framework for Discord bot functionality
- **Purpose**: Handles all Discord interactions, commands, and message management
- **Integration**: Used throughout the application for bot operations

## Python Standard Library
- **asyncio**: Asynchronous programming support for Discord bot operations
- **logging**: Comprehensive logging system for debugging and monitoring
- **uuid**: Unique identifier generation for events
- **datetime**: Timestamp management for events and participants
- **random**: Team randomization algorithms
- **enum**: Type-safe constants for event types and statuses

## Environment Configuration
- **DISCORD_BOT_TOKEN**: Required environment variable for Discord API authentication
- **Purpose**: Secure token storage for bot authorization

Note: The current implementation uses in-memory storage but is architected to easily integrate with database solutions like PostgreSQL with Drizzle ORM for persistent data storage.