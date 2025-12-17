#Streamlit application: Handles rendering, user input, and manages state - in memory database

import streamlit as st
from orchestrator import process_chat_turn

st.title("TalentScout Screening test")


GREETING="""Welcome to the TalentScout screening process.

This screening happens in two steps:
1. We’ll first collect some basic information about you.
2. Then you’ll be asked a few technical questions based on your profile.
Your responses will be reviewed by our hiring team.

Please reply only with the information requested in each question.
Keep your responses clear, professional, and relevant.

Let’s begin.

What is your full name?
"""

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": GREETING})


if "stage" not in st.session_state:
    st.session_state.stage="INFO_COLLECTION"

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "name":None,
        "email":None,
        "phone":None,
        "yoe":None,
        "desired_positions":[],
        "loc":None,
        "tech_stack":[]
    }
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Enter your response"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message = process_chat_turn(prompt, st.session_state.stage, st.session_state.candidate_data)
        st.write(message)
        st.session_state.messages.append({"role": "assistant", "content": message})