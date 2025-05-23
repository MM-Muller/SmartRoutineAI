# ui/streamlit_app.py

import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nlp import interpret_command
from core.scheduler import add_task, list_tasks, delete_task

st.set_page_config(page_title="SmartRoutine AI", layout="centered")
st.title("🧠 SmartRoutine AI")
st.subheader("Your intelligent personal assistant")

# --- Session state flags ---
if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# --- Command input ---
def handle_command():
    command = st.session_state.input_command
    result = interpret_command(command)

    if result["intent"] == "add_task":
        add_task(result["title"], result.get("datetime"))
        st.session_state.feedback = f"✅ Task added: {result['title']}"

    elif result["intent"] == "list_tasks":
        st.session_state.feedback = "📋 Listing tasks..."

    elif result["intent"] == "analyze_mood":
        st.session_state.feedback = "🧠 Mood analysis is under development."

    elif result["intent"] == "unknown":
        st.session_state.feedback = "⚠️ Command not recognized."

    # Clear input field
    st.session_state.input_command = ""

# Render input with on_change callback
st.text_input(
    "Enter a command (e.g., 'Add task Study at 6pm'):",
    key="input_command",
    on_change=handle_command
)

# Display feedback message (if any)
if st.session_state.feedback:
    st.info(st.session_state.feedback)
    st.session_state.feedback = ""

# --- Task list ---
st.divider()
st.subheader("📋 Pending Tasks")

# Handle task deletion with immediate update
deleted_task = st.query_params.get("deleted")
if deleted_task:
    st.query_params.clear()

tasks = list_tasks()
if tasks:
    for task in tasks:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"🕒 {task[2] or '--'} {task[3] or ''} — {task[1]}")
        with col2:
            if st.button("✔️ Done", key=f"done_{task[0]}"):
                delete_task(task[0])
                st.query_params["deleted"] = task[0]  # Update triggers rerun
                st.rerun()
else:
    st.write("No pending tasks.")