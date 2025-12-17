"""
TalentScout Orchestrator - Flow Control

This module manages the entire screening flow. It routes user input to appropriate agents
based on the current stage and updates application state.

Stages:
- INFO_COLLECTION: Gathering candidate information
- QUESTION_GENERATION: Creating technical questions
- ASK_QUESTIONS: Presenting questions and collecting answers
- ASSESSMENT: Evaluating candidate responses
- CONVO_END: Concluding the conversation
"""

from agents.info_collector import Info
from agents import info_collector, question_generator, evaluator
import streamlit as st
import time

# Required fields that must be collected from candidates
REQUIRED_FIELDS = [
    "name",
    "email",
    "phone",
    "yoe",
    "desired_positions",
    "loc",
    "tech_stack",
]

# Human-readable labels for fields
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
     """
     Check if all required candidate fields are filled.
     
     Args:
         candidate_data (dict): Candidate information dictionary
         
     Returns:
         bool: True if all required fields have values, False otherwise
     """
     return all(
         candidate_data.get(field) not in (None, [], "")
         for field in REQUIRED_FIELDS
     )


def process_chat_turn(user_input: str, current_stage: str, candidate_data):
     """
     Process a single turn of conversation based on current screening stage.
     
     Routes to appropriate agent and updates state.
     
     Args:
         user_input (str): User's message
         current_stage (str): Current screening stage
         candidate_data (dict): Current candidate information
         
     Returns:
         str: Response message to display to user
     """
    
    if user_input=="exit":
        #stop the chat. and give final response like thank you or something.
        exit

    if current_stage=="INFO_COLLECTION":
        #perform initial greeting and then ask user information 
        #run this IF block until stage changes to question generation

        with st.spinner("Processing your information..."):
            info_agent_response = info_collector.info_collection_agent(
                user_input, candidate_data
            )
        st.session_state.candidate_data |= info_agent_response
        if is_complete(st.session_state.candidate_data):
            st.session_state.stage = "QUESTION_GENERATION"
            st.write("All info collected! Generating Questions Now...")
            current_stage = "QUESTION_GENERATION"
            # Fall through to QUESTION_GENERATION block
        else:
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
            # Show instructions as a message
            instructions = ("You will now be asked technical questions based on your profile.\n\n"
                           "**Instructions:**\n"
                           "- Answer each question clearly and concisely\n"
                           "- Do not provide unnecessary information\n"
                           "- If unsure, share what you know")
            st.session_state.messages.append({"role": "assistant", "content": instructions})
            
            with st.spinner("Generating personalized questions..."):
                time.sleep(2)
                result = question_generator.question_generation_agent(st.session_state.candidate_data)
                st.session_state.questions = result["questions"]

            st.session_state.stage = "ASK_QUESTIONS"
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            
            time.sleep(1)
            question_text = f"Question 1 of {len(st.session_state.questions)}:\n\n{st.session_state.questions[0]}"
            return question_text

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
            # Add delay before showing next question
            with st.spinner("Loading next question..."):
                time.sleep(1.5)
            
            next_q = st.session_state.current_question_index
            return f"Question {next_q + 1} of {len(questions)}:\n\n{questions[next_q]}"
        else:
            st.session_state.stage = "ASSESSMENT"
            return "All questions answered. Evaluating your responses..."


    if current_stage=="ASSESSMENT":
        #after user has answered all the questions this IF block calls evaluator.py agent and perform evaluation of candidates
        #all the questions are now in session.questions

        with st.spinner("Evaluating your responses..."):
            evaluation = evaluator.assessment_agent(
                st.session_state.candidate_data,
                st.session_state.questions,
                st.session_state.answers
            )

        st.session_state.evaluation=evaluation
        st.session_state.stage = "CONVO_END"

        current_stage = "CONVO_END"


        

    if current_stage=="CONVO_END":
        #end conversation gracefully and tell user what happens next like hr will contact you and all
        return ("""
            Thank you for completing the screening.

            Your responses have been recorded and will be reviewed by our hiring team.
            If your profile matches our current requirements, someone from HR will reach out to you with the next steps.

            We appreciate your time and interest in the role.
        """)
