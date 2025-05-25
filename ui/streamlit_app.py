import streamlit as st
import sys, os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nlp import interpret_command
from core.scheduler import add_task, list_tasks, delete_task
from core.emotion_analysis import analyze_mood
from core.recommender import suggest_routine
from data.database import connect
from datetime import datetime

st.set_page_config(page_title="SmartRoutine AI", layout="centered")
st.title("🧠 SmartRoutine AI")
st.subheader("Your intelligent personal assistant")

# --- Session state flags ---
if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# Create placeholder for temporary messages
if "message_placeholder" not in st.session_state:
    st.session_state.message_placeholder = st.empty()

# --- Save mood to database ---
def save_mood_to_db(text, mood, confidence):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO moods (date, description, classification) VALUES (?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), text, f"{mood} ({confidence*100:.0f}%)")
        )
        conn.commit()

# Create tabs
tasks_tab, mood_tab, routine_tab = st.tabs(["📋 Tasks", "😊 Mood", "🧭 Routine"])

# --- Tasks Tab ---
with tasks_tab:
    st.subheader("Manage Your Tasks")
    
    # Initialize task_input in session state if not exists
    if "task_input" not in st.session_state:
        st.session_state.task_input = ""
    
    def add_task_callback():
        if st.session_state.task_input:
            result = interpret_command(st.session_state.task_input)
            if result["intent"] == "add_task":
                add_task(result["title"], result.get("datetime"))
                st.session_state.message_placeholder.success(f"✅ Task added: {result['title']}")
                st.session_state.task_input = ""
                time.sleep(1)
                st.session_state.message_placeholder.empty()
            else:
                st.session_state.message_placeholder.warning("⚠️ Please enter a valid task with time.")
                time.sleep(1)
                st.session_state.message_placeholder.empty()
    
    task_input = st.text_input(
        "Add a new task (e.g., 'Study at 6pm' or 'Meeting with team at 2pm'):",
        key="task_input"
    )
    
    st.button("Add Task", key="add_task_btn", on_click=add_task_callback)
    
    # Display tasks
    st.divider()
    st.subheader("📋 Pending Tasks")
    
    tasks = list_tasks()
    if tasks:
        for task in tasks:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"🕒 {task[2] or '--'} {task[3] or ''} — {task[1]}")
            with col2:
                if st.button("✔️ Done", key=f"done_{task[0]}"):
                    delete_task(task[0])
                    st.rerun()
    else:
        st.write("No pending tasks.")

# --- Mood Tab ---
with mood_tab:
    st.subheader("How are you feeling?")
    
    # Initialize mood_input in session state if not exists
    if "mood_input" not in st.session_state:
        st.session_state.mood_input = ""
    
    def analyze_mood_callback():
        if st.session_state.mood_input:
            mood_result = analyze_mood(st.session_state.mood_input)
            if "error" in mood_result:
                st.session_state.message_placeholder.error(f"❌ Error: {mood_result['error']}")
                time.sleep(3)
                st.session_state.message_placeholder.empty()
            else:
                emoji = "😄" if mood_result["mood"] == "positive" else "😞"
                st.session_state.message_placeholder.success(
                    f"{emoji} Mood: {mood_result['mood'].capitalize()}"
                    f" ({mood_result['confidence'] * 100:.0f}% confidence)"
                )
                save_mood_to_db(
                    mood_result["original_text"],
                    mood_result["mood"],
                    mood_result["confidence"]
                )
                st.session_state.mood_input = ""
                time.sleep(3)
                st.session_state.message_placeholder.empty()
    
    mood_input = st.text_area(
        "Describe how you're feeling today:",
        key="mood_input",
        height=100
    )
    
    st.button("Analyze Mood", key="analyze_mood_btn", on_click=analyze_mood_callback)
    
    # Display mood history
    st.divider()
    st.subheader("Mood History")
    
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, description, classification FROM moods ORDER BY id DESC LIMIT 10")
        moods = cursor.fetchall()
    
    if moods:
        for mood in moods:
            st.write(f"🗓️ {mood[0]} — _{mood[2]}_\n> {mood[1]}")
    else:
        st.write("No mood entries recorded yet.")

# --- Routine Tab ---
with routine_tab:
    st.subheader("Your Daily Routine")
    
    if st.button("🧭 Generate New Routine Suggestion"):
        suggestion = suggest_routine()
        st.session_state.routine_suggestion = suggestion
        st.rerun()
    
    if "routine_suggestion" in st.session_state:
        st.markdown(f"### 🧭 Suggested Routine\n> {st.session_state.routine_suggestion}")
    else:
        st.info("Click the button above to get a personalized routine suggestion!")
