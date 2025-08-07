"""
Timezone utilities for French time (UTC+2) handling
"""

from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

# French timezone UTC+2 (summer time in France)
FRANCE_OFFSET = timedelta(hours=2)
FRANCE_TZ = timezone(FRANCE_OFFSET)

def get_france_time():
    """Get current time in France timezone"""
    return datetime.now(FRANCE_TZ)

def get_utc_time():
    """Get current UTC time"""
    return datetime.now(timezone.utc)

def parse_french_datetime(date_str: str, time_str: str) -> datetime:
    """
    Parse French date and time strings to UTC datetime
    
    Args:
        date_str: Date in DD/MM/YYYY format
        time_str: Time in HH:MM format
    
    Returns:
        datetime object in UTC
    """
    try:
        # Parse the date and time
        day, month, year = map(int, date_str.split('/'))
        hour, minute = map(int, time_str.split(':'))
        
        # Create datetime with French timezone
        france_dt = datetime(year, month, day, hour, minute, tzinfo=FRANCE_TZ)
        
        # Convert to UTC and return as naive datetime
        utc_dt = france_dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        logger.info(f"Parsed {date_str} {time_str} (France UTC+2) -> {utc_dt} (UTC)")
        return utc_dt
        
    except Exception as e:
        logger.error(f"Error parsing French datetime '{date_str} {time_str}': {e}")
        raise ValueError(f"Format de date/heure invalide. Utilisez DD/MM/YYYY HH:MM")

def format_french_datetime(utc_dt: datetime) -> str:
    """
    Format UTC datetime to French display format
    
    Args:
        utc_dt: UTC datetime object
    
    Returns:
        Formatted string in French timezone
    """
    try:
        # Convert UTC to French time
        utc_dt_aware = utc_dt.replace(tzinfo=timezone.utc)
        france_dt = utc_dt_aware.astimezone(FRANCE_TZ)
        
        # Format in French style
        return france_dt.strftime('%d/%m/%Y à %H:%M')
        
    except Exception as e:
        logger.error(f"Error formatting datetime {utc_dt}: {e}")
        return utc_dt.strftime('%d/%m/%Y à %H:%M')

def get_time_until_event_french(event_utc_time: datetime) -> tuple:
    """
    Get time remaining until event in French timezone
    
    Args:
        event_utc_time: Event time in UTC
    
    Returns:
        tuple: (time_remaining_timedelta, french_time_string)
    """
    try:
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        time_remaining = event_utc_time - now_utc
        
        # Format event time in French
        french_time = format_french_datetime(event_utc_time)
        
        return time_remaining, french_time
        
    except Exception as e:
        logger.error(f"Error calculating time until event: {e}")
        return timedelta(0), "Erreur de calcul"

def validate_french_date_format(date_str: str) -> bool:
    """Validate DD/MM/YYYY format"""
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return False
        
        day, month, year = map(int, parts)
        
        # Basic validation
        if not (1 <= day <= 31 and 1 <= month <= 12 and 2024 <= year <= 2030):
            return False
            
        return True
    except:
        return False

def validate_french_time_format(time_str: str) -> bool:
    """Validate HH:MM format"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
        
        hour, minute = map(int, parts)
        
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False
            
        return True
    except:
        return False