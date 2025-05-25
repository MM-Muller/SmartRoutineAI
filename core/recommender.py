# core/recommender.py

from datetime import datetime
from data.database import connect  # <- Import corrigido

def get_latest_mood():
    """Retrieve the latest mood entry from the database."""
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT classification FROM moods ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0].split(" ")[0].lower()  # Extract mood type (e.g., 'positive')
    return None

def suggest_routine():
    """Suggest a routine based on the latest mood and time of day."""
    mood = get_latest_mood()
    now = datetime.now().hour

    if mood == "positive":
        if 6 <= now <= 10:
            return "You're in a great mood! Start your day with a walk or journaling."
        elif 12 <= now <= 14:
            return "Feeling good? Take advantage and tackle something important now."
        else:
            return "Enjoy the rest of your day. Maybe plan something creative."

    elif mood == "negative":
        if 6 <= now <= 10:
            return "Take your morning slow. Try stretching and drink some water."
        elif 12 <= now <= 14:
            return "Feeling down? Consider a short break or a calming activity."
        else:
            return "Rest is valid. Unplug and try something light like music or tea."

    return "No recent mood detected. How are you feeling today?"
