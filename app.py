"""
TalentScout Screening Chatbot - Main Application Interface

This module handles the Streamlit UI, user input management, and session state.
It displays the chatbot interface and manages the conversation flow by calling the orchestrator.
"""

import streamlit as st
from orchestrator import process_chat_turn

st.title("TalentScout Screening test")

# Sidebar with exit option
with st.sidebar:
    st.write("### Options")
    if st.button("Exit Screening"):
        st.session_state.stage = "CONVO_END"
        st.write("Thank you for your time. Screening ended.")
        st.stop()

# Initial greeting message for candidates
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

# Initialize session state variables if not present
if "openai_model" not in st.session_state:
     st.session_state["openai_model"] = "gpt-3.5-turbo"

# Message history for conversation
if "messages" not in st.session_state:
     st.session_state.messages = []
     st.session_state.messages.append({"role": "assistant", "content": GREETING})

# Current screening stage
if "stage" not in st.session_state:
     st.session_state.stage="INFO_COLLECTION"

# Candidate information being collected
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
# Display all messages in conversation history
for message in st.session_state.messages:
     with st.chat_message(message["role"]):
         st.markdown(message["content"])

# Chat input disabled when screening is complete
if prompt := st.chat_input("Enter your response", disabled=st.session_state.stage=="CONVO_END"):
     # Add user message to history
     st.session_state.messages.append({"role": "user", "content": prompt})
     with st.chat_message("user"):
         st.markdown(prompt)
     
     # Process user input through orchestrator and display response
     with st.chat_message("assistant"):
         message = process_chat_turn(prompt, st.session_state.stage, st.session_state.candidate_data)
         st.write(message)
         st.session_state.messages.append({"role": "assistant", "content": message})



        