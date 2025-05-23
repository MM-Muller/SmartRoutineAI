import re
from datetime import datetime

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
    # Basic datetime parsing for expressions like 'at 5pm' or 'on monday'
    time_match = re.search(r"at (\d{1,2})(am|pm)?", text)
    if time_match:
        hour = int(time_match.group(1))
        meridian = time_match.group(2)
        if meridian == "pm" and hour < 12:
            hour += 12
        return datetime.now().replace(hour=hour, minute=0).isoformat()
    return None
