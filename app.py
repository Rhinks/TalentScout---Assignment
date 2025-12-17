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

# --- 2. CUSTOM CSS STYLING (FORCE DARK THEME) ---
def load_css():
    st.markdown("""
        <style>
            /* --- GLOBAL DARK THEME OVERRIDES --- */
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            
            [data-testid="stSidebar"] {
                background-color: #262730;
                border-right: 1px solid #41444C;
            }

            /* --- CHAT BUBBLES --- */
            .stChatMessage {
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 15px;
                border: 1px solid #41444C;
            }

            /* Assistant Message (Dark Grey) */
            div[data-testid="stChatMessage"]:nth-child(odd) {
                background-color: #1F2937;
                border-color: #374151;
            }
            
            /* User Message (Navy Blue Accent) */
            div[data-testid="stChatMessage"]:nth-child(even) {
                background-color: #1E3A8A;
                border-color: #1E40AF;
                color: #E0E7FF;
            }

            /* --- TEXT & HEADERS --- */
            h1, h2, h3 { color: #F3F4F6 !important; }
            p, div, span { color: #E5E7EB; }

            /* Custom Header */
            .main-header {
                text-align: center;
                padding: 10px 0 20px 0;
                color: #60A5FA !important;
                font-weight: 700;
            }

            /* Success/Exit Box */
            .success-box {
                background-color: #064E3B;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #059669;
                margin-top: 20px;
            }
            
            /* Hide Default Streamlit Elements */
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

# Initialize candidate data container
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "name": None,
        "email": None,
        # Other fields are managed by orchestrator but not shown in UI
    }

# Initial greeting message
GREETING = """
### 👋 Welcome to TalentScout

I am your AI Hiring Assistant. I will conduct a brief screening to gather your information and assess your technical skills.

**The Process:**
1.  **Info Collection:** I'll ask for your basic details (Name, Email, Stack, etc.).
2.  **Technical Round:** I'll generate questions based on your tech stack.

Let's begin. **What is your full name?**
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": GREETING})

# --- 4. SIMPLIFIED SIDEBAR (Name & Email Only) ---
with st.sidebar:
    st.title("TalentScout")
    st.markdown("---")
    
    st.subheader("Candidate Details")
    
    # Simple display of Name and Email
    # We use .get() to safely retrieve data without errors
    c_name = st.session_state.candidate_data.get('name')
    c_email = st.session_state.candidate_data.get('email')

    if c_name:
        st.markdown(f"**👤 Name:** \n{c_name}")
    else:
        st.markdown("**👤 Name:** \n*Pending...*")
        
    st.markdown("") # Spacer

    if c_email:
        st.markdown(f"**📧 Email:** \n{c_email}")
    else:
        st.markdown("**📧 Email:** \n*Pending...*")

    st.markdown("---")
    
    # Exit Option (Requirement: "Exit whenever conversation-ending keyword is encountered" OR manual exit)
    if st.button("End Interview", type="primary"):
        st.session_state.stage = "CONVO_END"
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---

st.markdown("<h1 class='main-header'>AI Screening Portal</h1>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. INPUT HANDLING ---

if st.session_state.stage == "CONVO_END":
    # Graceful Conclusion
    st.markdown("""
        <div class='success-box'>
            <h3 style='color: #A7F3D0 !important; margin:0;'>Session Concluded</h3>
            <p style='color: #D1FAE5 !important;'>Thank you for your time. Your responses have been recorded for review.</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Chat Input
    if prompt := st.chat_input("Type your response..."):
        
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. Assistant Logic
        with st.chat_message("assistant", avatar="🤖"):
            # Direct call to orchestrator (No extra spinners to avoid conflicts)
            response_message = process_chat_turn(
                prompt, 
                st.session_state.stage, 
                st.session_state.candidate_data
            )
            st.write(response_message)
        
        st.session_state.messages.append({"role": "assistant", "content": response_message})
        
        # Check if the orchestrator decided to end the chat based on the response
        if st.session_state.stage == "CONVO_END":
            st.rerun()