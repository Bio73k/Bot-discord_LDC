"""
Service for managing Destiny 2 clan events
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging
from models.event import Event
from utils.constants import EventType, EventStatus

logger = logging.getLogger(__name__)

class EventService:
    """Service to manage clan events"""
    
    def __init__(self):
        # In-memory storage for MVP
        # In production, this would be replaced with a database
        self._events: Dict[str, Event] = {}
        self._message_to_event: Dict[int, str] = {}  # Maps message IDs to event IDs
    
    def create_event(
        self,
        event_type: EventType,
        name: str,
        description: str,
        creator_id: int,
        guild_id: int,
        max_participants: int = 100,
        event_date=None,
        team_size: Optional[int] = None
    ) -> Event:
        """Create a new event"""
        try:
            # Generate unique event ID
            event_id = str(uuid.uuid4())[:8]  # Short ID for user convenience
            
            # Create event
            event = Event(
                event_id=event_id,
                event_type=event_type,
                name=name,
                description=description,
                creator_id=creator_id,
                guild_id=guild_id,
                max_participants=max_participants,
                event_date=event_date
            )
            
            # Set team size if provided
            if team_size is not None:
                event.team_size = team_size
            
            # Store event
            self._events[event_id] = event
            
            logger.info(f"Created event: {event_id} - {name}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID"""
        return self._events.get(event_id)
    
    def get_event_by_message_id(self, message_id: int) -> Optional[Event]:
        """Get an event by Discord message ID"""
        event_id = self._message_to_event.get(message_id)
        if event_id:
            return self.get_event(event_id)
        
        # Fallback: search through all events
        for event in self._events.values():
            if event.message_id == message_id:
                self._message_to_event[message_id] = event.event_id
                return event
        
        return None
    
    def link_message_to_event(self, message_id: int, event_id: str):
        """Link a Discord message ID to an event ID"""
        self._message_to_event[message_id] = event_id
    
    def get_events_by_guild(self, guild_id: int) -> List[Event]:
        """Get all events for a specific guild"""
        return [
            event for event in self._events.values()
            if event.guild_id == guild_id
        ]
    
    def get_events_by_creator(self, creator_id: int, guild_id: int) -> List[Event]:
        """Get all events created by a specific user in a guild"""
        return [
            event for event in self._events.values()
            if event.creator_id == creator_id and event.guild_id == guild_id
        ]
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            if event_id in self._events:
                event = self._events[event_id]
                
                # Remove message mapping if exists
                if event.message_id:
                    self._message_to_event.pop(event.message_id, None)
                
                # Remove event
                del self._events[event_id]
                
                logger.info(f"Deleted event: {event_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            return False
    
    def add_participant(self, event_id: str, user_id: int) -> bool:
        """Add a participant to an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            success = event.add_participant(user_id)
            
            if success:
                logger.info(f"User {user_id} joined event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add participant to event {event_id}: {e}")
            return False
    
    def remove_participant(self, event_id: str, user_id: int) -> bool:
        """Remove a participant from an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            success = event.remove_participant(user_id)
            
            if success:
                logger.info(f"User {user_id} left event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove participant from event {event_id}: {e}")
            return False
    
    def enable_check_in(self, event_id: str, start_time=None, end_time=None) -> bool:
        """Enable check-in for an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            event.enable_check_in(start_time, end_time)
            logger.info(f"Enabled check-in for event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable check-in for event {event_id}: {e}")
            return False
    
    def disable_check_in(self, event_id: str) -> bool:
        """Disable check-in for an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            event.disable_check_in()
            logger.info(f"Disabled check-in for event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable check-in for event {event_id}: {e}")
            return False
    
    def check_in_participant(self, event_id: str, user_id: int) -> bool:
        """Check in a participant to an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            success = event.check_in_participant(user_id)
            if success:
                logger.info(f"User {user_id} checked in to event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to check in user {user_id} to event {event_id}: {e}")
            return False
    
    def check_out_participant(self, event_id: str, user_id: int) -> bool:
        """Check out a participant from an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            success = event.check_out_participant(user_id)
            if success:
                logger.info(f"User {user_id} checked out from event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to check out user {user_id} from event {event_id}: {e}")
            return False
    
    def get_attendance_report(self, event_id: str) -> Optional[dict]:
        """Get attendance report for an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return None
            
            return {
                'event_id': event_id,
                'event_name': event.name,
                'total_participants': event.participant_count,
                'checked_in_count': event.checked_in_count,
                'attendance_rate': event.attendance_rate,
                'checked_in_participants': event.checked_in_participants,
                'no_show_participants': event.get_no_show_participants(),
                'check_in_enabled': event.check_in_enabled,
                'check_in_active': event.is_check_in_active()
            }
            
        except Exception as e:
            logger.error(f"Failed to get attendance report for event {event_id}: {e}")
            return None
    
    def is_participant(self, event_id: str, user_id: int) -> bool:
        """Check if a user is a participant in an event"""
        event = self.get_event(event_id)
        if not event:
            return False
        
        return event.is_participant(user_id)
    
    def get_participant_count(self, event_id: str) -> int:
        """Get the number of participants in an event"""
        event = self.get_event(event_id)
        if not event:
            return 0
        
        return event.participant_count
    
    def update_event_status(self, event_id: str, status: EventStatus) -> bool:
        """Update an event's status"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            event.status = status
            logger.info(f"Updated event {event_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update event status: {e}")
            return False
    
    def get_events_by_status(self, guild_id: int, status: EventStatus) -> List[Event]:
        """Get events by status for a guild"""
        return [
            event for event in self.get_events_by_guild(guild_id)
            if event.status == status
        ]
    
    def get_events_by_type(self, guild_id: int, event_type: EventType) -> List[Event]:
        """Get events by type for a guild"""
        return [
            event for event in self.get_events_by_guild(guild_id)
            if event.event_type == event_type
        ]
    
    def cleanup_old_events(self, days: int = 7) -> int:
        """
        Clean up events older than specified days
        Returns number of events cleaned up
        """
        try:
            cutoff_date = datetime.utcnow().replace(
                day=datetime.utcnow().day - days
            )
            
            old_events = [
                event_id for event_id, event in self._events.items()
                if event.created_at < cutoff_date
            ]
            
            cleaned_count = 0
            for event_id in old_events:
                if self.delete_event(event_id):
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old events")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0
    
    def get_event_statistics(self, guild_id: int) -> dict:
        """Get statistics for events in a guild"""
        events = self.get_events_by_guild(guild_id)
        
        stats = {
            'total_events': len(events),
            'by_type': {},
            'by_status': {},
            'total_participants': 0,
            'average_participants': 0
        }
        
        if not events:
            return stats
        
        # Count by type
        for event_type in EventType:
            count = len([e for e in events if e.event_type == event_type])
            stats['by_type'][event_type.value] = count
        
        # Count by status
        for status in EventStatus:
            count = len([e for e in events if e.status == status])
            stats['by_status'][status.value] = count
        
        # Participant statistics
        total_participants = sum(e.participant_count for e in events)
        stats['total_participants'] = total_participants
        stats['average_participants'] = total_participants / len(events) if events else 0
        
        return stats
