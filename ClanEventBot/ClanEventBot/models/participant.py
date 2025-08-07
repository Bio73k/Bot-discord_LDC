"""
Participant model for events
"""

from datetime import datetime
from typing import Optional

class Participant:
    """Represents a participant in a Destiny 2 event"""
    
    def __init__(self, user_id: int, event_id: str):
        self.user_id = user_id
        self.event_id = event_id
        self.joined_at = datetime.utcnow()
        self.team_number: Optional[int] = None
    
    @property
    def is_assigned_to_team(self) -> bool:
        """Check if participant is assigned to a team"""
        return self.team_number is not None
    
    def assign_to_team(self, team_number: int):
        """Assign participant to a team"""
        self.team_number = team_number
    
    def remove_from_team(self):
        """Remove participant from their current team"""
        self.team_number = None
    
    def to_dict(self) -> dict:
        """Convert participant to dictionary for serialization"""
        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'joined_at': self.joined_at.isoformat(),
            'team_number': self.team_number
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Participant':
        """Create participant from dictionary"""
        participant = cls(
            user_id=data['user_id'],
            event_id=data['event_id']
        )
        
        participant.joined_at = datetime.fromisoformat(data['joined_at'])
        participant.team_number = data.get('team_number')
        
        return participant
    
    def __str__(self) -> str:
        team_info = f" (Team {self.team_number})" if self.team_number else ""
        return f"Participant({self.user_id}){team_info}"
    
    def __repr__(self) -> str:
        return (
            f"Participant(user_id={self.user_id}, event_id='{self.event_id}', "
            f"team_number={self.team_number})"
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Participant):
            return False
        return self.user_id == other.user_id and self.event_id == other.event_id
    
    def __hash__(self) -> int:
        return hash((self.user_id, self.event_id))
