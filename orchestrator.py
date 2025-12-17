"""
TalentScout Orchestrator - Flow Control
"""

from agents import info_collector, question_generator, evaluator
import streamlit as st
import time

REQUIRED_FIELDS = ["name", "email", "phone", "yoe", "desired_positions", "loc", "tech_stack"]

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
     return all(candidate_data.get(field) not in (None, [], "") for field in REQUIRED_FIELDS)

def process_chat_turn(user_input: str, current_stage: str, candidate_data):
    
    if user_input == "exit":
        return "Thank you for your time. Screening ended."

    # --- STAGE 1: INFO COLLECTION ---
    if st.session_state.stage == "INFO_COLLECTION":
        with st.spinner("Processing your information..."):
            info_agent_response = info_collector.info_collection_agent(
                user_input, candidate_data
            )
        
        # Update data
        st.session_state.candidate_data.update(info_agent_response)
        
        # Check completion
        if is_complete(st.session_state.candidate_data):
            st.session_state.stage = "QUESTION_GENERATION"
            # NO RETURN HERE - Fall through to the next block immediately
        else:
            missing = [f for f in REQUIRED_FIELDS if st.session_state.candidate_data.get(f) in (None, [], "")]
            missing_labels = [FIELD_LABELS.get(f, f) for f in missing]
            return (
                "Thank you.\n\n"
                "To continue, I still need the following details:\n"
                f"- {', '.join(missing_labels)}\n\n"
                "Please provide them in your next reply."
            )

    # --- STAGE 2: QUESTION GENERATION ---
    if st.session_state.stage == "QUESTION_GENERATION":
        # 1. Define Instructions
        instructions = (
            "**Profile Complete! Moving to Technical Assessment.**\n\n"
            "**Instructions:**\n"
            "- I will generate technical questions based on your stack.\n"
            "- Answer clearly and concisely.\n"
            "- If you don't know an answer, simply type 'Pass'.\n\n"
            "Generating your unique questions now..."
        )
        
        # 2. Display Instructions IMMEDIATELY so user can read them
        st.markdown(instructions)
        
        # 3. Save instructions to history manually (since we aren't returning them)
        # We check to ensure we don't duplicate if this code runs twice
        if st.session_state.messages[-1]["content"] != instructions:
            st.session_state.messages.append({"role": "assistant", "content": instructions})

        # 4. Run Spinner (User reads instructions while this happens)
        with st.spinner("Analyzing tech stack and generating questions..."):
            # time.sleep(2) # Optional: artificial delay if API is too fast, to let user read
            result = question_generator.question_generation_agent(st.session_state.candidate_data)
            st.session_state.questions = result["questions"]

        # 5. Set up Quiz State
        st.session_state.stage = "ASK_QUESTIONS"
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        
        # 6. Return ONLY the first question (app.py will display this)
        first_q = st.session_state.questions[0]
        return f"**Question 1 of {len(st.session_state.questions)}:**\n\n{first_q}"

    # --- STAGE 3: ASK QUESTIONS ---
    if st.session_state.stage == "ASK_QUESTIONS":
        
        # Get current state
        q_idx = st.session_state.current_question_index
        questions = st.session_state.questions
        
        # Store the answer to the PREVIOUS question
        # We use the question text as the key to be safe
        current_q_text = questions[q_idx]
        st.session_state.answers[current_q_text] = user_input
        
        # Increment
        st.session_state.current_question_index += 1
        new_idx = st.session_state.current_question_index

        # Check if there are more questions
        if new_idx < len(questions):
            with st.spinner("Recording answer and loading next question..."):
                time.sleep(1) # Small UX pause
            
            next_q = questions[new_idx]
            return f"**Question {new_idx + 1} of {len(questions)}:**\n\n{next_q}"
        else:
            # Quiz done, fall through to assessment
            st.session_state.stage = "ASSESSMENT"
            # Fall through immediately

    # --- STAGE 4: ASSESSMENT ---
    if st.session_state.stage == "ASSESSMENT":
        with st.spinner("Analyzing your technical responses..."):
            evaluation = evaluator.assessment_agent(
                st.session_state.candidate_data,
                st.session_state.questions,
                st.session_state.answers
            )

        st.session_state.evaluation = evaluation
        st.session_state.stage = "CONVO_END"

    # --- STAGE 5: CONCLUSION ---
    if st.session_state.stage == "CONVO_END":
        return ("""
            Thank you for completing the screening.

            Your responses have been recorded and will be reviewed by our hiring team.
            If your profile matches our requirements, we will reach out shortly.

            **Screening Complete.**
        """)