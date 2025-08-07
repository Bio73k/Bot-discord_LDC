"""
Service for managing teams in Destiny 2 events
"""

import random
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TeamService:
    """Service to manage team assignments for events"""
    
    def __init__(self):
        pass
    
    def randomize_teams(
        self,
        participant_ids: List[int],
        team_size: int
    ) -> List[List[int]]:
        """
        Randomize participants into teams of specified size
        
        Args:
            participant_ids: List of participant user IDs
            team_size: Number of players per team
            
        Returns:
            List of teams, where each team is a list of user IDs
            
        Raises:
            ValueError: If team_size is invalid or no participants provided
        """
        if not participant_ids:
            raise ValueError("No participants to assign to teams")
        
        if team_size not in [1, 2, 3, 4, 6]:
            raise ValueError("Team size must be 1, 2, 3, 4, or 6 players")
        
        if len(participant_ids) < 1:
            raise ValueError(f"Not enough participants for teams")
        
        # For team size 1, we don't need minimum participants check
        if team_size > 1 and len(participant_ids) < team_size:
            raise ValueError(f"Not enough participants for teams of size {team_size}")
        
        try:
            # Shuffle participants for random assignment
            shuffled_participants = participant_ids.copy()
            random.shuffle(shuffled_participants)
            
            # Create teams
            teams = []
            for i in range(0, len(shuffled_participants), team_size):
                team = shuffled_participants[i:i + team_size]
                
                # Only add complete teams
                if len(team) == team_size:
                    teams.append(team)
            
            logger.info(f"Created {len(teams)} teams of size {team_size}")
            
            # Log if there are leftover participants
            total_assigned = len(teams) * team_size
            leftover = len(participant_ids) - total_assigned
            if leftover > 0:
                logger.info(f"{leftover} participants could not be assigned to complete teams")
            
            return teams
            
        except Exception as e:
            logger.error(f"Failed to randomize teams: {e}")
            raise
    
    def create_balanced_teams(
        self,
        participant_ids: List[int],
        team_size: int,
        allow_incomplete: bool = False
    ) -> List[List[int]]:
        """
        Create balanced teams with option to allow incomplete teams
        
        Args:
            participant_ids: List of participant user IDs
            team_size: Number of players per team
            allow_incomplete: Whether to allow incomplete teams
            
        Returns:
            List of teams, where each team is a list of user IDs
        """
        if not participant_ids:
            raise ValueError("No participants to assign to teams")
        
        if team_size not in [1, 2, 3, 4, 6]:
            raise ValueError("Team size must be 1, 2, 3, 4, or 6 players")
        
        try:
            # Shuffle participants
            shuffled_participants = participant_ids.copy()
            random.shuffle(shuffled_participants)
            
            teams = []
            
            # Create complete teams first
            complete_teams_count = len(shuffled_participants) // team_size
            for i in range(complete_teams_count):
                start_idx = i * team_size
                end_idx = start_idx + team_size
                teams.append(shuffled_participants[start_idx:end_idx])
            
            # Handle remaining participants
            remaining_start = complete_teams_count * team_size
            remaining_participants = shuffled_participants[remaining_start:]
            
            if remaining_participants and allow_incomplete:
                # Add remaining participants as an incomplete team
                teams.append(remaining_participants)
            elif remaining_participants and not allow_incomplete:
                # Distribute remaining participants to existing teams
                for i, participant in enumerate(remaining_participants):
                    if teams:  # Only if we have teams to add to
                        team_index = i % len(teams)
                        teams[team_index].append(participant)
            
            logger.info(f"Created {len(teams)} balanced teams")
            return teams
            
        except Exception as e:
            logger.error(f"Failed to create balanced teams: {e}")
            raise
    
    def redistribute_teams(
        self,
        current_teams: List[List[int]],
        new_team_size: int
    ) -> List[List[int]]:
        """
        Redistribute existing teams into new team size
        
        Args:
            current_teams: Current team assignments
            new_team_size: New desired team size
            
        Returns:
            New team assignments with the specified size
        """
        if not current_teams:
            raise ValueError("No current teams to redistribute")
        
        if new_team_size not in [1, 2, 3, 4, 6]:
            raise ValueError("Team size must be 1, 2, 3, 4, or 6 players")
        
        try:
            # Flatten all participants from current teams
            all_participants = []
            for team in current_teams:
                all_participants.extend(team)
            
            # Create new teams with the new size
            return self.randomize_teams(all_participants, new_team_size)
            
        except Exception as e:
            logger.error(f"Failed to redistribute teams: {e}")
            raise
    
    def validate_teams(self, teams: List[List[int]], expected_team_size: int) -> dict:
        """
        Validate team assignments
        
        Args:
            teams: List of teams to validate
            expected_team_size: Expected size for each team
            
        Returns:
            Validation results dictionary
        """
        validation = {
            'is_valid': True,
            'issues': [],
            'stats': {
                'total_teams': len(teams),
                'total_participants': 0,
                'complete_teams': 0,
                'incomplete_teams': 0,
                'duplicate_participants': []
            }
        }
        
        if not teams:
            validation['is_valid'] = False
            validation['issues'].append("No teams provided")
            return validation
        
        all_participants = []
        
        for i, team in enumerate(teams):
            team_number = i + 1
            team_size = len(team)
            
            # Check team size
            if team_size == expected_team_size:
                validation['stats']['complete_teams'] += 1
            else:
                validation['stats']['incomplete_teams'] += 1
                validation['issues'].append(f"Team {team_number} has {team_size} players (expected {expected_team_size})")
            
            # Check for empty teams
            if team_size == 0:
                validation['is_valid'] = False
                validation['issues'].append(f"Team {team_number} is empty")
            
            # Track all participants for duplicate checking
            all_participants.extend(team)
        
        # Check for duplicate participants
        seen = set()
        for participant in all_participants:
            if participant in seen:
                validation['stats']['duplicate_participants'].append(participant)
                validation['is_valid'] = False
                validation['issues'].append(f"Participant {participant} is assigned to multiple teams")
            seen.add(participant)
        
        validation['stats']['total_participants'] = len(all_participants)
        
        return validation
    
    def get_team_assignments(self, teams: List[List[int]]) -> dict:
        """
        Get a mapping of participants to their team numbers
        
        Args:
            teams: List of teams
            
        Returns:
            Dictionary mapping participant ID to team number (1-indexed)
        """
        assignments = {}
        
        for team_index, team in enumerate(teams):
            team_number = team_index + 1
            for participant in team:
                assignments[participant] = team_number
        
        return assignments
    
    def shuffle_teams(self, teams: List[List[int]]) -> List[List[int]]:
        """
        Shuffle the order of teams (not participants within teams)
        
        Args:
            teams: Current team assignments
            
        Returns:
            Teams in shuffled order
        """
        shuffled_teams = teams.copy()
        random.shuffle(shuffled_teams)
        return shuffled_teams
    
    def get_team_statistics(self, teams: List[List[int]]) -> dict:
        """
        Get statistics about team distribution
        
        Args:
            teams: List of teams
            
        Returns:
            Statistics dictionary
        """
        if not teams:
            return {
                'total_teams': 0,
                'total_participants': 0,
                'average_team_size': 0,
                'min_team_size': 0,
                'max_team_size': 0,
                'team_sizes': []
            }
        
        team_sizes = [len(team) for team in teams]
        total_participants = sum(team_sizes)
        
        return {
            'total_teams': len(teams),
            'total_participants': total_participants,
            'average_team_size': total_participants / len(teams),
            'min_team_size': min(team_sizes) if team_sizes else 0,
            'max_team_size': max(team_sizes) if team_sizes else 0,
            'team_sizes': team_sizes
        }
