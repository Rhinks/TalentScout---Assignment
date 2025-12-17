"""
TalentScout Screening Chatbot - Main Application Interface
"""

import streamlit as st
from orchestrator import process_chat_turn

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS STYLING ---
def load_css():
    st.markdown("""
        <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            [data-testid="stSidebar"] {
                background-color: #262730;
                border-right: 1px solid #41444C;
            }
            .stChatMessage {
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 15px;
                border: 1px solid #41444C;
            }
            div[data-testid="stChatMessage"]:nth-child(odd) {
                background-color: #1F2937;
                border-color: #374151;
            }
            div[data-testid="stChatMessage"]:nth-child(even) {
                background-color: #1E3A8A;
                border-color: #1E40AF;
                color: #E0E7FF;
            }
            h1, h2, h3 { color: #F3F4F6 !important; }
            .main-header {
                text-align: center;
                padding: 10px 0 20px 0;
                color: #60A5FA !important;
                font-weight: 700;
            }
            .success-box {
                background-color: #064E3B;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #059669;
                margin-bottom: 20px;
            }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- 3. SESSION STATE INITIALIZATION ---
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
if "stage" not in st.session_state:
    st.session_state.stage = "INFO_COLLECTION"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {"name": None, "email": None}

# IMPROVED GREETING
GREETING = """
### 👋 Welcome to TalentScout

I am your AI Hiring Assistant. I will conduct an initial screening to learn more about your background and assess your technical expertise for our open roles.

**The Process:**
1. **Information Gathering:** I will collect your professional profile details, including your experience, current location, and tech stack.
2. **Technical Assessment:** I will generate 3-5 technical questions tailored specifically to the tech stack you provide to evaluate your proficiency.

Your responses will be shared directly with our hiring team for review.

**Let's begin. What is your full name?**
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("TalentScout")
    st.markdown("---")
    
    # Check if the evaluation has been completed by the orchestrator
    if "evaluation" in st.session_state:
        eval_data = st.session_state.evaluation
        score = eval_data.get('score', 0)
        verdict = eval_data.get('verdict', 'N/A')
        summary = eval_data.get('summary', '') # ADDED SUMMARY

        st.metric(label="Technical Score", value=f"{score}/10")
        
        if verdict == "PASS":
            st.success(f"Verdict: {verdict}")
        elif verdict == "BORDERLINE":
            st.warning(f"Verdict: {verdict}")
        else:
            st.error(f"Verdict: {verdict}")
        
        # ADDED SUMMARY DISPLAY
        if summary:
            st.markdown(f"**Assessment Summary:**\n{summary}")
            
        st.markdown("---")
    
    st.subheader("Candidate Details")
    c_name = st.session_state.candidate_data.get('name')
    c_email = st.session_state.candidate_data.get('email')
    st.markdown(f"**👤 Name:** \n{c_name if c_name else '*Pending...*'}")
    st.markdown(f"**📧 Email:** \n{c_email if c_email else '*Pending...*'}")

    st.markdown("---")
    if st.button("End Interview", type="primary"):
        st.session_state.stage = "CONVO_END"
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.markdown("<h1 class='main-header'>AI Screening Portal</h1>", unsafe_allow_html=True)

if st.session_state.stage == "CONVO_END":
    st.markdown("""
        <div class='success-box'>
            <h3 style='color: #A7F3D0 !important; margin:0;'>Session Concluded</h3>
            <p style='color: #D1FAE5 !important;'>Thank you for your time. Your assessment is complete.</p>
        </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. INPUT HANDLING ---
if st.session_state.stage != "CONVO_END":
    if prompt := st.chat_input("Type your response..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            response_message = process_chat_turn(
                prompt, 
                st.session_state.stage, 
                st.session_state.candidate_data
            )
            st.write(response_message)
        
        st.session_state.messages.append({"role": "assistant", "content": response_message})
        if st.session_state.stage == "CONVO_END":
            st.rerun()