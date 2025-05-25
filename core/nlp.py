import re
from datetime import datetime, timedelta

def interpret_command(text):
    """
    Analyzes a command and returns a dictionary with the detected intent and any relevant information.
    """
    text = text.lower().strip()

    # Check for task creation intent
    if "add task" in text or "create task" in text:
        return {
            "intent": "add_task",
            "title": extract_task_title(text),
            "datetime": extract_datetime(text)
        }

    # Check for task listing
    if "what are my tasks" in text or "list tasks" in text:
        return {
            "intent": "list_tasks"
        }

    # Mood analysis request
    if "i feel" in text or "mood" in text:
        return {
            "intent": "analyze_mood",
            "text": text
        }

    # Default fallback
    return {
        "intent": "unknown",
        "raw": text
    }

def extract_task_title(text):
    # Very basic heuristic – improve this with NLP later
    match = re.search(r"(add|create) task (.+?)( at| on|$)", text)
    if match:
        return match.group(2).strip()
    return "Untitled Task"

def extract_datetime(text):
    # Get current date and time
    now = datetime.now()
    
    # Dictionary for weekday mapping
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    # Map month names to numbers
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Try different date patterns
    date_patterns = [
        # "on May 26" or "on the 26th of May"
        r'on (?:the )?(\d{1,2})(?:st|nd|rd|th)?(?: of)? ([a-zA-Z]+)',
        # "on 26 May"
        r'on (\d{1,2}) ([a-zA-Z]+)',
        # "on May 26th"
        r'on ([a-zA-Z]+) (\d{1,2})(?:st|nd|rd|th)?',
        # "on 26/05" or "on 05/26"
        r'on (\d{1,2})/(\d{1,2})',
        # "on 26-05" or "on 05-26"
        r'on (\d{1,2})-(\d{1,2})',
        # "on 26.05" or "on 05.26"
        r'on (\d{1,2})\.(\d{1,2})'
    ]
    
    target_date = None
    
    # Try each date pattern
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            groups = date_match.groups()
            
            # Handle different date formats
            if len(groups) == 2:
                # Check if first group is month name
                if groups[0].lower() in months:
                    month = months[groups[0].lower()]
                    day = int(groups[1])
                # Check if second group is month name
                elif groups[1].lower() in months:
                    month = months[groups[1].lower()]
                    day = int(groups[0])
                # Assume DD/MM format
                else:
                    # Try to determine if it's DD/MM or MM/DD
                    first = int(groups[0])
                    second = int(groups[1])
                    if first > 12:  # Definitely DD/MM
                        day = first
                        month = second
                    elif second > 12:  # Definitely MM/DD
                        day = second
                        month = first
                    else:  # Ambiguous, assume DD/MM
                        day = first
                        month = second
                
                # Create target date with current year
                target_date = datetime(now.year, month, day)
                # If the date has passed, move to next year
                if target_date < now:
                    target_date = target_date.replace(year=now.year + 1)
                break
    
    # If no specific date found, try weekday
    if not target_date:
        weekday_match = re.search(r'(on|this|next) (monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)', text)
        if weekday_match:
            prefix = weekday_match.group(1)
            weekday = weekday_match.group(2)
            days_ahead = weekdays[weekday] - now.weekday()
            
            # Adjust for "next week"
            if prefix == 'next':
                days_ahead += 7
            elif prefix == 'this' and days_ahead < 0:
                days_ahead += 7
                
            target_date = now + timedelta(days=days_ahead)
        else:
            target_date = now
    
    # Try to match time
    time_match = re.search(r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridian = time_match.group(3)
        
        # Convert to 24-hour format
        if meridian:
            if meridian == 'pm' and hour < 12:
                hour += 12
            elif meridian == 'am' and hour == 12:
                hour = 0
        
        # Set the time
        target_date = target_date.replace(hour=hour, minute=minute)
        
        # If the time has passed for today and no specific date was given, move to next day
        if target_date < now and not date_match:
            target_date += timedelta(days=1)
            
        return target_date.isoformat()
    
    return None
