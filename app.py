import os
import json
import queue
import time
import requests
import numpy as np
import streamlit as st
from vosk import Model, KaldiRecognizer
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, RTCConfiguration

# ==============================
# CONFIG
# ==============================
OLLAMA_MODEL = "phi3:mini"
OLLAMA_URL = "http://localhost:11434/api/generate"
VOSK_MODEL_PATH = "models/vosk"

st.set_page_config(layout="centered", page_title="AI Control", page_icon="🧠")

# ==============================
# SESSION STATE
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "processing" not in st.session_state:
    st.session_state.processing = False

# ==============================
# THEME COLORS
# ==============================
if st.session_state.theme == "dark":
    BG = "#0b0b0f"
    PANEL = "rgba(255,215,0,0.05)"
    BORDER = "rgba(255,215,0,0.15)"
    TEXT = "#d4af37"
    SUBTEXT = "#888"
else:
    BG = "#111111"
    PANEL = "rgba(0,0,0,0.05)"
    BORDER = "rgba(0,0,0,0.1)"
    TEXT = "#c9a227"
    SUBTEXT = "#555"

# ==============================
# PREMIUM STYLING
# ==============================
st.markdown(f"""
<style>
#MainMenu, footer, header {{visibility:hidden;}}

.stApp {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', sans-serif;
}}

.panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px;
    margin-top: 20px;
    backdrop-filter: blur(10px);
}}

input {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}

button {{
    border-radius: 8px !important;
}}

.core {{
    width: 140px;
    height: 140px;
    border-radius: 50%;
    margin: auto;
    border: 2px solid {TEXT};
    animation: spin 6s linear infinite;
    box-shadow: 0 0 30px {TEXT};
}}

@keyframes spin {{
    100% {{ transform: rotate(360deg); }}
}}

.processing {{
    box-shadow: 0 0 60px gold;
}}

.title {{
    text-align:center;
    font-size:24px;
    margin-top:15px;
}}

.chatbox {{
    max-height:300px;
    overflow-y:auto;
}}

.user {{ text-align:right; }}
.bot {{ text-align:left; color:#aaa; }}

</style>
""", unsafe_allow_html=True)

# ==============================
# AI CORE
# ==============================
core_class = "core processing" if st.session_state.processing else "core"
st.markdown(f'<div class="{core_class}"></div>', unsafe_allow_html=True)
st.markdown('<div class="title">AI CORE SYSTEM</div>', unsafe_allow_html=True)

# ==============================
# THEME TOGGLE
# ==============================
if st.button("Toggle Dark / Light Mode"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

# ==============================
# FUNCTIONS
# ==============================
def ask_ollama(prompt):
    st.session_state.processing = True
    st.rerun()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120
        )
        reply = r.json()["response"]
    except:
        reply = "Ollama not running."

    st.session_state.processing = False
    return reply

def execute_command(text):
    text = text.lower()
    if "open calculator" in text:
        os.system("start calc")
        return "Opening Calculator..."
    if "open google" in text:
        os.system("start https://google.com")
        return "Opening Google..."
    return ask_ollama(text)

# ==============================
# COMMAND PANEL
# ==============================
st.markdown('<div class="panel">', unsafe_allow_html=True)

user_input = st.text_input("Enter Command", label_visibility="collapsed")

col1, col2 = st.columns(2)

with col1:
    if st.button("Execute"):
        if user_input:
            st.session_state.history.append(("You", user_input))
            reply = execute_command(user_input)
            st.session_state.history.append(("AI", reply))

with col2:
    if st.button("Clear"):
        st.session_state.history = []

st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# CHAT
# ==============================
st.markdown('<div class="panel chatbox">', unsafe_allow_html=True)

for role, msg in st.session_state.history:
    if role == "You":
        st.markdown(f'<div class="user"><b>{role}:</b> {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot"><b>{role}:</b> {msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# STATUS
# ==============================
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.write("Model:", OLLAMA_MODEL)
st.write("Mode: Offline")
st.markdown('</div>', unsafe_allow_html=True)