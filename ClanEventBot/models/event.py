"""
Event model for Destiny 2 clan events
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from utils.constants import EventType, EventStatus

class Event:
    """Represents a Destiny 2 clan event"""
    
    def __init__(
        self,
        event_id: str,
        event_type: EventType,
        name: str,
        description: str,
        creator_id: int,
        guild_id: int,
        max_participants: int = 100,
        event_date: Optional[datetime] = None
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.guild_id = guild_id
        self.max_participants = max_participants
        self.created_at = datetime.utcnow()
        self.event_date = event_date  # Optional scheduled date/time for the event
        self.status = EventStatus.OPEN
        
        # Participant management
        self.participants: List[int] = []
        self.checked_in_participants: List[int] = []  # Participants who checked in
        
        # Team management
        self.teams: List[List[int]] = []
        self.team_size: Optional[int] = None
        
        # Discord message tracking
        self.message_id: Optional[int] = None
        self.thread_id: Optional[int] = None
        
        # Notification tracking
        self.reminder_sent: bool = False
        
        # Check-in system
        self.check_in_enabled: bool = False
        self.check_in_start_time: Optional[datetime] = None
        self.check_in_end_time: Optional[datetime] = None
    
    @property
    def participant_count(self) -> int:
        """Get the current number of participants"""
        return len(self.participants)
    
    @property
    def checked_in_count(self) -> int:
        """Get the number of participants who checked in"""
        return len(self.checked_in_participants)
    
    @property
    def attendance_rate(self) -> float:
        """Get the attendance rate as a percentage"""
        if self.participant_count == 0:
            return 0.0
        return (self.checked_in_count / self.participant_count) * 100
    
    @property
    def is_full(self) -> bool:
        """Check if the event is at capacity"""
        return self.participant_count >= self.max_participants
    
    @property
    def has_teams(self) -> bool:
        """Check if teams have been assigned"""
        return bool(self.teams)
    
    @property
    def team_count(self) -> int:
        """Get the number of teams"""
        return len(self.teams)
    
    def add_participant(self, user_id: int) -> bool:
        """
        Add a participant to the event
        Returns True if successful, False if already in or event is full
        """
        if user_id in self.participants:
            return False
        
        if self.is_full:
            return False
        
        self.participants.append(user_id)
        
        # Update status if event becomes full
        if self.is_full:
            self.status = EventStatus.FULL
        
        return True
    
    def remove_participant(self, user_id: int) -> bool:
        """
        Remove a participant from the event
        Returns True if successful, False if not in event
        """
        if user_id not in self.participants:
            return False
        
        self.participants.remove(user_id)
        
        # Remove from teams if they were assigned
        for team in self.teams:
            if user_id in team:
                team.remove(user_id)
                break
        
        # Update status if event is no longer full
        if self.status == EventStatus.FULL and not self.is_full:
            self.status = EventStatus.OPEN
        
        return True
    
    def is_participant(self, user_id: int) -> bool:
        """Check if a user is a participant in the event"""
        return user_id in self.participants
    
    def is_checked_in(self, user_id: int) -> bool:
        """Check if a participant has checked in"""
        return user_id in self.checked_in_participants
    
    def check_in_participant(self, user_id: int) -> bool:
        """
        Check in a participant
        Returns True if successful, False if not a participant or already checked in
        """
        # Must be a participant to check in
        if not self.is_participant(user_id):
            return False
        
        # Can't check in if not enabled
        if not self.check_in_enabled:
            return False
        
        # Check if check-in period is active
        now = datetime.utcnow()
        if self.check_in_start_time and now < self.check_in_start_time:
            return False
        if self.check_in_end_time and now > self.check_in_end_time:
            return False
        
        # Already checked in
        if user_id in self.checked_in_participants:
            return False
        
        self.checked_in_participants.append(user_id)
        return True
    
    def check_out_participant(self, user_id: int) -> bool:
        """
        Check out a participant (remove from checked in list)
        Returns True if successful, False if not checked in
        """
        if user_id not in self.checked_in_participants:
            return False
        
        self.checked_in_participants.remove(user_id)
        return True
    
    def enable_check_in(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        """Enable check-in for the event with optional time window"""
        self.check_in_enabled = True
        self.check_in_start_time = start_time
        self.check_in_end_time = end_time
    
    def disable_check_in(self):
        """Disable check-in for the event"""
        self.check_in_enabled = False
    
    def is_check_in_active(self) -> bool:
        """Check if check-in is currently active"""
        if not self.check_in_enabled:
            return False
        
        now = datetime.utcnow()
        if self.check_in_start_time and now < self.check_in_start_time:
            return False
        if self.check_in_end_time and now > self.check_in_end_time:
            return False
        
        return True
    
    def get_no_show_participants(self) -> List[int]:
        """Get list of participants who didn't check in"""
        return [user_id for user_id in self.participants if user_id not in self.checked_in_participants]
    
    def get_team_for_participant(self, user_id: int) -> Optional[int]:
        """Get the team number for a participant (1-indexed)"""
        for i, team in enumerate(self.teams):
            if user_id in team:
                return i + 1
        return None
    
    def clear_teams(self):
        """Clear all team assignments"""
        self.teams = []
        self.team_size = None
    
    def set_teams(self, teams: List[List[int]], team_size: int):
        """Set the team assignments"""
        self.teams = teams
        self.team_size = team_size
    
    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'guild_id': self.guild_id,
            'max_participants': self.max_participants,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'participants': self.participants,
            'checked_in_participants': self.checked_in_participants,
            'teams': self.teams,
            'team_size': self.team_size,
            'message_id': self.message_id,
            'check_in_enabled': self.check_in_enabled,
            'check_in_start_time': self.check_in_start_time.isoformat() if self.check_in_start_time else None,
            'check_in_end_time': self.check_in_end_time.isoformat() if self.check_in_end_time else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create event from dictionary"""
        event = cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            name=data['name'],
            description=data['description'],
            creator_id=data['creator_id'],
            guild_id=data['guild_id'],
            max_participants=data.get('max_participants', 100)
        )
        
        event.created_at = datetime.fromisoformat(data['created_at'])
        event.status = EventStatus(data['status'])
        event.participants = data.get('participants', [])
        event.checked_in_participants = data.get('checked_in_participants', [])
        event.teams = data.get('teams', [])
        event.team_size = data.get('team_size')
        event.message_id = data.get('message_id')
        event.check_in_enabled = data.get('check_in_enabled', False)
        
        # Parse check-in times
        if data.get('check_in_start_time'):
            event.check_in_start_time = datetime.fromisoformat(data['check_in_start_time'])
        if data.get('check_in_end_time'):
            event.check_in_end_time = datetime.fromisoformat(data['check_in_end_time'])
        
        return event
    
    def __str__(self) -> str:
        return f"Event({self.event_id}): {self.name} - {self.event_type.value}"
    
    def __repr__(self) -> str:
        return (
            f"Event(event_id='{self.event_id}', name='{self.name}', "
            f"type={self.event_type}, participants={self.participant_count})"
        )
