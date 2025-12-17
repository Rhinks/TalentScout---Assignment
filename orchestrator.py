# Manages entire conversation flow
# routes user input to the correct agent, and updates the state
from agents.info_collector import Info
from agents import info_collector, question_generator
import streamlit as st

REQUIRED_FIELDS = [
    "name",
    "email",
    "phone",
    "yoe",
    "desired_positions",
    "loc",
    "tech_stack",
]

FIELD_LABELS = {
    "name":"name",
    "email": "email address",
    "phone": "phone number",
    "yoe": "years of experience",
    "desired_positions": "desired role",
    "loc": "current location",
    "tech_stack": "technology stack"
}


def is_complete(candidate_data: dict) -> bool:
    return all(
        candidate_data.get(field) not in (None, [], "")
        for field in REQUIRED_FIELDS
    )


def process_chat_turn(user_input:str, current_stage:str, candidate_data):
    
    if user_input=="exit":
        #stop the chat. and give final response like thank you or something.
        exit

    if current_stage=="INFO_COLLECTION":
        #perform initial greeting and then ask user information 
        #run this IF block until stage changes to question generation

        info_agent_response = info_collector.info_collection_agent(
            user_input, candidate_data
        )
        st.session_state.candidate_data |= info_agent_response
        if is_complete(st.session_state.candidate_data):
            st.session_state.stage = "QUESTION_GENERATION"
            return "All info collected! Generating Questions Now..."
        
        missing = [
            f for f in REQUIRED_FIELDS
            if st.session_state.candidate_data.get(f) in (None, [], "")
        ]
        missing_labels =  [FIELD_LABELS.get(f, f) for f in missing]
        return (
            "Thank you for your response.\n\n"
            "To continue with the screening process, I still need the following information:\n"
            f"- {', '.join(missing_labels)}\n\n"
            "Please provide only the requested details in your next reply so we can move forward."
        )


            

    if current_stage == "QUESTION_GENERATION":
        if "questions" not in st.session_state:
            result = question_generator.question_generation_agent(
                st.session_state.candidate_data
            )
            st.session_state.questions = result["questions"]

        st.session_state.stage = "ASK_QUESTIONS"
        return (
            "Your screening questions are ready.\n\n"
            "You’ll be asked a few questions one by one. "
            "Please answer each question clearly and conscisely. If you’re unsure, share what you know. "
            
        )


    if current_stage == "ASK_QUESTIONS":
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
            st.session_state.answers = {}

            # Ask first question
            return f"Question 1:\n\n{st.session_state.questions[0]}"

        q_idx = st.session_state.current_question_index
        questions = st.session_state.questions

        # Store answer to previous question
        st.session_state.answers[q_idx] = user_input
        st.session_state.current_question_index += 1

        # Ask next question or move on
        if st.session_state.current_question_index < len(questions):
            next_q = st.session_state.current_question_index
            return f"Question {next_q + 1}:\n\n{questions[next_q]}"
        else:
            st.session_state.stage = "ASSESSMENT"
            return "All questions answered. Evaluating your responses..."


    if current_stage=="ASSESSMENT":
        #after user has answered all the questions this IF block calls evaluator.py agent and perform evaluation of candidates
        #all the questions are now in session.questions
        pass
        


    if current_stage=="CONVO_END":
        #end conversation gracefully and tell user what happens next like hr will contact you and all
        pass

    
    



        
        
