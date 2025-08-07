"""
Service for managing event reminders and notifications
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import discord
from services.event_service import EventService

logger = logging.getLogger(__name__)

class ReminderService:
    """Service to handle event reminders and notifications"""
    
    def __init__(self, bot, event_service: EventService):
        self.bot = bot
        self.event_service = event_service
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the reminder service"""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._reminder_loop())
            logger.info("Reminder service started")
    
    async def stop(self):
        """Stop the reminder service"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Reminder service stopped")
    
    async def _reminder_loop(self):
        """Main loop to check for upcoming events"""
        while self._running:
            try:
                await self._check_upcoming_events()
                # Check every 15 seconds for better timing precision
                await asyncio.sleep(15)
            except Exception as e:
                logger.error(f"Error in reminder loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_upcoming_events(self):
        """Check for events starting in 2 minutes and send reminders"""
        now = datetime.utcnow()
        events_count = len(self.event_service._events)
        
        # Only log details if there are events
        if events_count > 0:
            logger.info(f"Current time: {now}")
            logger.info(f"Checking {events_count} events")
        
        for event in self.event_service._events.values():
            # Debug logging for each event
            if events_count > 0:
                logger.info(f"Event {event.event_id}: date={event.event_date}, reminder_sent={event.reminder_sent}, thread_id={event.thread_id}, participants={len(event.participants)}")
            
            # Skip if no scheduled date/time or reminder already sent
            if not event.event_date or event.reminder_sent:
                if events_count > 0:
                    logger.info(f"Skipping event {event.event_id}: no_date={not event.event_date}, reminder_sent={event.reminder_sent}")
                continue
            
            # Calculate time until event
            time_until_event = event.event_date - now
            logger.info(f"Event {event.event_id} starts in: {time_until_event}")
            
            # Send reminder if event starts in 2 minutes for testing (normally 10 minutes)
            # Wider window to ensure we don't miss it: 30s to 3 minutes
            if timedelta(seconds=30) <= time_until_event <= timedelta(minutes=3):
                logger.info(f"Sending reminder for event {event.event_id} - starts in {time_until_event}")
                await self._send_event_reminder(event)
                event.reminder_sent = True
    
    async def _send_event_reminder(self, event):
        """Send reminder message and team creation request to event participants"""
        try:
            # Find the thread for this event
            if not event.thread_id:
                logger.warning(f"No thread ID for event {event.event_id}, cannot send reminder")
                return
                
            # Get the thread channel
            thread = self.bot.get_channel(event.thread_id)
            if not thread:
                # Try to fetch it if not in cache
                try:
                    thread = await self.bot.fetch_channel(event.thread_id)
                except Exception:
                    logger.error(f"Could not find or fetch thread {event.thread_id} for event {event.event_id}")
                    return
            
            # Create reminder message with participant mentions
            if not event.participants:
                logger.info(f"No participants to remind for event {event.event_id}")
                return
                
            participant_mentions = [f"<@{user_id}>" for user_id in event.participants]
            mentions_text = " ".join(participant_mentions)
            
            reminder_message = (
                f"🔔 **Rappel d'événement !**\n\n"
                f"{mentions_text}\n\n"
                f"L'événement **{event.name}** commence bientôt !\n\n"
                f"Préparez-vous les gardiens ! 🎮"
            )
            
            await thread.send(reminder_message)
            logger.info(f"Sent reminder for event {event.event_id} to {len(event.participants)} participants in thread {event.thread_id}")
            
            # Send team creation request to event creator
            await self._send_team_creation_request(event, thread)
        
        except Exception as e:
            logger.error(f"Failed to send reminder for event {event.event_id}: {e}")
            # Log additional details for debugging
            logger.error(f"Event thread_id: {getattr(event, 'thread_id', 'None')}")
            logger.error(f"Participant count: {len(getattr(event, 'participants', []))}")
    
    async def _send_team_creation_request(self, event, thread):
        """Send interactive team size selection to event creator"""
        try:
            # Skip if teams already exist
            if event.teams:
                logger.info(f"Teams already exist for event {event.event_id}, skipping auto-creation")
                return
            
            # Skip if not enough participants for teams
            if len(event.participants) < 2:
                logger.info(f"Not enough participants for teams in event {event.event_id} ({len(event.participants)} participants)")
                return
            
            from utils.team_selection_view import TeamSizeSelectionView
            
            # Create the selection embed
            embed = discord.Embed(
                title="⚔️ Création automatique d'équipes",
                description=(
                    f"**Événement :** {event.name}\n"
                    f"**Participants :** {len(event.participants)}\n\n"
                    f"<@{event.creator_id}>, choisissez la taille des équipes pour cet événement :\n\n"
                    f"🎯 **1 joueur** - Défis solo\n"
                    f"👥 **2 joueurs** - Crucible, Gambit\n"
                    f"🔺 **3 joueurs** - Épreuves, Donjons\n"
                    f"🔷 **4 joueurs** - Assauts\n"
                    f"⭐ **6 joueurs** - Raids\n\n"
                    f"*Vous avez 5 minutes pour choisir.*"
                ),
                color=0x00bfff
            )
            
            # Create the view with buttons
            view = TeamSizeSelectionView(event, self.bot)
            
            # Send the message with the view
            message = await thread.send(embed=embed, view=view)
            view.message = message  # Store message reference for timeout editing
            
            logger.info(f"Sent team creation request for event {event.event_id} to creator {event.creator_id}")
            
        except Exception as e:
            logger.error(f"Failed to send team creation request for event {event.event_id}: {e}")