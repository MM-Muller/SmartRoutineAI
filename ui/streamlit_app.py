import streamlit as st
import sys, os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nlp import interpret_command
from core.scheduler import add_task, list_tasks, delete_task
from core.emotion_analysis import analyze_mood
from core.recommender import suggest_routine
from data.database import connect
from datetime import datetime, timedelta
from voice.voice_input import VoiceRecognizer, VoiceInputError
from voice.voice_out import VoiceOutput
from core.calendar_integration import (
    listar_eventos_google_calendar,
    criar_evento_google_calendar,
    deletar_evento_google_calendar,
    CalendarError
)

st.set_page_config(page_title="SmartRoutine AI", layout="centered")
st.title("🧠 SmartRoutine AI")
st.subheader("Your intelligent personal assistant")

# --- Session state flags ---
if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "voice_recognizer" not in st.session_state:
    st.session_state.voice_recognizer = VoiceRecognizer()

if "voice_output" not in st.session_state:
    st.session_state.voice_output = VoiceOutput()

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
tasks_tab, mood_tab, routine_tab, calendar_tab = st.tabs(["📋 Tasks", "😊 Mood", "🧭 Routine", "📅 Calendar"])

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
                st.session_state.voice_output.speak(f"Task added: {result['title']}")
                st.session_state.task_input = ""
                time.sleep(1)
                st.session_state.message_placeholder.empty()
            else:
                st.session_state.message_placeholder.warning("⚠️ Please enter a valid task with time.")
                st.session_state.voice_output.speak("Please enter a valid task with time.")
                time.sleep(1)
                st.session_state.message_placeholder.empty()
    
    def voice_input_callback():
        try:
            st.session_state.message_placeholder.info("🎙️ Listening...")
            st.session_state.voice_output.speak("Listening...")
            texto, confianca = st.session_state.voice_recognizer.ouvir_comando(mostrar_feedback=False)
            
            if confianca >= 0.6:
                st.session_state.task_input = texto
                st.session_state.message_placeholder.success(f"✅ Recognized: {texto}")
                st.session_state.voice_output.speak(f"Recognized: {texto}")
                time.sleep(1)
                st.session_state.message_placeholder.empty()
            else:
                st.session_state.message_placeholder.warning(f"⚠️ Low confidence ({confianca:.2%}). Please try again.")
                st.session_state.voice_output.speak("Low confidence. Please try again.")
                time.sleep(2)
                st.session_state.message_placeholder.empty()
                
        except VoiceInputError as e:
            st.session_state.message_placeholder.error(f"❌ Error: {str(e)}")
            st.session_state.voice_output.speak(f"Error: {str(e)}")
            time.sleep(2)
            st.session_state.message_placeholder.empty()
    
    # Create two columns for text input and voice button
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        task_input = st.text_input(
            "Add/Create task (e.g., 'Team Meeting on June 15 at 2pm' or 'Project Review on 20/06 at 10am'):",
            key="task_input"
        )
    
    with col2:
        st.button("🎙️ Voice Input", key="voice_input_btn", on_click=voice_input_callback)
    
    st.button("Add Task", key="add_task_btn", on_click=add_task_callback)
    
    # Display tasks
    st.divider()
    st.subheader("📋 Pending Tasks")
    
    tasks = list_tasks()
    if tasks:
        for task in tasks:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # Parse the datetime string
                try:
                    if task[2]:  # if datetime exists
                        task_datetime = datetime.fromisoformat(task[2])
                        # Format the date and time
                        date_str = task_datetime.strftime("%A, %B %d")  # e.g., "Monday, January 1"
                        time_str = task_datetime.strftime("%I:%M %p")   # e.g., "09:00 AM"
                        st.write(f"📅 {date_str} at {time_str} — {task[1]}")
                    else:
                        st.write(f"⏰ No time set — {task[1]}")
                except (ValueError, TypeError):
                    st.write(f"⏰ {task[2] or 'No time set'} — {task[1]}")
            with col2:
                if st.button("✔️ Done", key=f"done_{task[0]}"):
                    delete_task(task[0])
                    st.session_state.voice_output.speak(f"Task completed: {task[1]}")
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
                st.session_state.voice_output.speak(f"Error: {mood_result['error']}")
                time.sleep(3)
                st.session_state.message_placeholder.empty()
            else:
                emoji = "😄" if mood_result["mood"] == "positive" else "😞"
                mood_message = f"{emoji} Mood: {mood_result['mood'].capitalize()} ({mood_result['confidence'] * 100:.0f}% confidence)"
                st.session_state.message_placeholder.success(mood_message)
                st.session_state.voice_output.speak(f"Your mood is {mood_result['mood']}")
                save_mood_to_db(
                    mood_result["original_text"],
                    mood_result["mood"],
                    mood_result["confidence"]
                )
                st.session_state.mood_input = ""
                time.sleep(3)
                st.session_state.message_placeholder.empty()
    
    def voice_mood_callback():
        try:
            st.session_state.message_placeholder.info("🎙️ Listening...")
            st.session_state.voice_output.speak("Listening...")
            texto, confianca = st.session_state.voice_recognizer.ouvir_comando(mostrar_feedback=False)
            
            if confianca >= 0.6:
                st.session_state.mood_input = texto
                st.session_state.message_placeholder.success(f"✅ Recognized: {texto}")
                st.session_state.voice_output.speak(f"Recognized: {texto}")
                time.sleep(1)
                st.session_state.message_placeholder.empty()
            else:
                st.session_state.message_placeholder.warning(f"⚠️ Low confidence ({confianca:.2%}). Please try again.")
                st.session_state.voice_output.speak("Low confidence. Please try again.")
                time.sleep(2)
                st.session_state.message_placeholder.empty()
                
        except VoiceInputError as e:
            st.session_state.message_placeholder.error(f"❌ Error: {str(e)}")
            st.session_state.voice_output.speak(f"Error: {str(e)}")
            time.sleep(2)
            st.session_state.message_placeholder.empty()
    
    # Create two columns for text input and voice button
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        mood_input = st.text_area(
            "Describe how you're feeling today:",
            key="mood_input",
            height=100
        )
    
    with col2:
        st.button("🎙️ Voice Input", key="voice_mood_btn", on_click=voice_mood_callback)
    
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
        st.session_state.voice_output.speak("Here's your new routine suggestion")
        st.rerun()
    
    if "routine_suggestion" in st.session_state:
        st.markdown(f"### 🧭 Suggested Routine\n> {st.session_state.routine_suggestion}")
    else:
        st.info("Click the button above to get a personalized routine suggestion!")

# --- Calendar Tab ---
with calendar_tab:
    st.subheader("Google Calendar Integration")
    
    # Botão para sincronizar tarefas com o Google Calendar
    if st.button("🔄 Sync Tasks with Calendar"):
        try:
            tasks = list_tasks()
            for task in tasks:
                if task[2]:  # se tiver datetime
                    try:
                        task_datetime = datetime.fromisoformat(task[2])
                        criar_evento_google_calendar(
                            titulo=task[1],
                            data_hora_inicio=task_datetime,
                            duracao_min=30,
                            descricao=f"Task from SmartRoutine AI: {task[1]}"
                        )
                    except (ValueError, TypeError) as e:
                        st.warning(f"Could not sync task '{task[1]}': Invalid datetime format")
                    except CalendarError as e:
                        st.error(f"Error syncing task '{task[1]}': {str(e)}")
            
            st.success("✅ Tasks synchronized with Google Calendar!")
            st.session_state.voice_output.speak("Tasks synchronized with Google Calendar")
            time.sleep(2)
            st.rerun()
            
        except CalendarError as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.voice_output.speak(f"Error: {str(e)}")
    
    # Seção para visualizar eventos do calendário
    st.divider()
    st.subheader("📅 Upcoming Events")
    
    try:
        # Opções de período
        periodo = st.selectbox(
            "Select time period:",
            ["Today", "Next 7 days", "Next 30 days"]
        )
        
        # Define o período baseado na seleção
        data_inicio = datetime.now()
        if periodo == "Today":
            data_fim = data_inicio + timedelta(days=1)
        elif periodo == "Next 7 days":
            data_fim = data_inicio + timedelta(days=7)
        else:  # Next 30 days
            data_fim = data_inicio + timedelta(days=30)
        
        # Busca eventos
        eventos = listar_eventos_google_calendar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            max_resultados=50
        )
        
        if eventos:
            for evento in eventos:
                # Extrai informações do evento
                inicio = datetime.fromisoformat(evento['start'].get('dateTime', evento['start'].get('date')))
                fim = datetime.fromisoformat(evento['end'].get('dateTime', evento['end'].get('date')))
                
                # Formata a data e hora
                data_str = inicio.strftime("%A, %B %d")
                hora_str = inicio.strftime("%I:%M %p")
                
                # Cria um container para cada evento
                with st.container():
                    col1, col2 = st.columns([0.8, 0.2])
                    
                    with col1:
                        st.write(f"📅 {data_str} at {hora_str}")
                        st.write(f"**{evento['summary']}**")
                        if evento.get('description'):
                            st.write(f"_{evento['description']}_")
                        if evento.get('location'):
                            st.write(f"📍 {evento['location']}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{evento['id']}"):
                            try:
                                deletar_evento_google_calendar(evento['id'])
                                st.success("✅ Event deleted!")
                                st.session_state.voice_output.speak("Event deleted")
                                time.sleep(1)
                                st.rerun()
                            except CalendarError as e:
                                st.error(f"❌ Error: {str(e)}")
                                st.session_state.voice_output.speak(f"Error: {str(e)}")
                    
                    st.divider()
        else:
            st.info("No events found for the selected period.")
            st.session_state.voice_output.speak("No events found for the selected period")
            
    except CalendarError as e:
        st.error(f"❌ Error accessing Google Calendar: {str(e)}")
        st.session_state.voice_output.speak(f"Error accessing Google Calendar: {str(e)}")
        st.info("Please make sure you have configured your Google Calendar credentials correctly.")
