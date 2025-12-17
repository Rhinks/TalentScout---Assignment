# TalentScout - Hiring Screening Chatbot

## Project Overview

TalentScout is a technical screening chatbot built to streamline the initial hiring process. It automates candidate information collection and technical assessment through a conversational interface.

The chatbot:
- Gathers candidate information (name, email, contact, experience, tech stack)
- Generates tailored technical questions based on declared skills
- Evaluates candidate responses
- Provides feedback on screening completion

This is designed for small to medium-scale recruitment processes where initial technical screening needs to be efficient and consistent.

## Features

- **Information Collection**: Gathers candidate details through conversation
- **Adaptive Questions**: Generates 3-5 technical questions based on candidate's tech stack and experience level
- **Technical Assessment**: Evaluates answers for correctness and depth
- **User-Friendly Interface**: Simple chat-based interaction via Streamlit
- **Graceful Exit**: Users can exit screening at any point
- **Off-Topic Handling**: Redirects candidates back to screening scope

## Installation

### Prerequisites
- Python 3.12+
- pip or uv package manager
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd TalentScout_Assignment
   ```

2. **Set up virtual environment with uv** (recommended)
   ```bash
   uv sync
   source .venv/bin/activate
   ```
   
   Or with pip:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   Create a `.env` file in the project root:
   ```
   OPENAI_API=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

The chatbot will be accessible at `http://localhost:8501`

## Usage Guide

### Starting the Screening
1. Open the Streamlit app
2. Read the welcome greeting and instructions
3. Provide your full name when prompted

### Information Collection Phase
- Answer questions about your email, phone, experience, desired roles, location, and tech stack
- The chatbot will ask for missing information until all fields are complete
- Responses are processed and validated in real-time

### Technical Questions Phase
- After information collection, you'll receive 3-5 technical questions
- Questions are tailored to your declared tech stack and experience level
- Answer each question clearly and concisely
- There's a brief delay between questions for better UX

### Screening Completion
- After answering all questions, your responses are evaluated
- You'll receive a completion message with next steps
- The input field is disabled to prevent further responses

### Early Exit
- Click the "Exit Screening" button in the sidebar to end the conversation at any time

## Technical Details

### Architecture

The system follows a modular agent-based architecture:

```
app.py (UI/State Management)
    ↓
orchestrator.py (Flow Control)
    ├── info_collector.py (Info extraction agent)
    ├── question_generator.py (Question generation agent)
    └── evaluator.py (Response evaluation agent)
```

### Technology Stack

- **Frontend**: Streamlit 1.x
- **LLM**: OpenAI GPT-4o-2024-08-06
- **Language**: Python 3.12
- **Data Validation**: Pydantic
- **Package Manager**: uv

### Key Files

- `app.py`: Main Streamlit application, UI and session state management
- `orchestrator.py`: Orchestrates flow between stages (INFO_COLLECTION → QUESTION_GENERATION → ASK_QUESTIONS → ASSESSMENT → CONVO_END)
- `agents/info_collector.py`: Extracts candidate information using LLM
- `agents/question_generator.py`: Generates adaptive technical questions
- `agents/evaluator.py`: Evaluates candidate responses and provides scores
- `config.py`: Configuration constants
- `.env`: API keys and sensitive configuration (not tracked in git)

### Data Flow

1. User input is processed by orchestrator
2. Based on current stage, appropriate agent is called
3. LLM response is parsed and structured using Pydantic models
4. State is updated in `st.session_state`
5. Response is displayed to user and added to message history

## Prompt Design

### Information Collection Prompt

The info_collector agent is instructed to:
- Extract only explicitly provided information
- Avoid guessing or inferring missing details
- Redirect off-topic questions back to the screening
- Return structured JSON with only newly extracted fields

This ensures data accuracy and prevents hallucination.

### Question Generation Prompt

The question_generator agent uses:
- **Adaptive Difficulty Matrix**: Adjusts question complexity based on years of experience
  - 0-2 years: Basic syntax and API usage
  - 3-5 years: Common pitfalls and frameworks
  - 5+ years: Performance, internals, and security
- **Question Constraints**: Max 20 words, specific and factual
- **Tech Stack Focus**: Generates questions only for declared technologies

Example: For a Python Junior with Django, questions focus on list methods, Django ORM basics, etc.

### Evaluation Prompt

The evaluator assesses answers based on:
- Correctness and accuracy
- Clarity of explanation
- Evidence of practical experience
- Scoring rubric (0-10 scale)
- Verdict rules (PASS ≥7, BORDERLINE 4-6, FAIL ≤3)

## Challenges & Solutions

### Challenge 1: Multi-turn Context
**Problem**: Initial implementation treated each turn independently, losing context.
**Solution**: Maintain full message history in `st.session_state` and pass to agents. This allows coherent follow-up questions and better information gathering.

### Challenge 2: Stage Transitions Without User Input
**Problem**: After info collection completes, chatbot required user input before moving to question generation.
**Solution**: Implement fall-through logic in orchestrator—when a stage changes, continue processing the new stage in the same function call instead of returning early.

### Challenge 3: Message Persistence on Rerun
**Problem**: Questions and instructions vanished on Streamlit rerun when using `st.write()`.
**Solution**: Add messages to `st.session_state.messages` directly so they persist in message history across reruns.

### Challenge 4: LLM Output Validation
**Problem**: LLM sometimes returned partial or invalid JSON structures.
**Solution**: Used Pydantic models with Optional fields and `exclude_none=True` to handle partial data gracefully.

### Challenge 5: Data Privacy
**Problem**: Sensitive candidate data (email, phone) stored in plain text.
**Solution**: Current implementation stores in session state (cleared on app restart). For production, implement:
- Hashing or encryption for sensitive fields
- Secure database with access controls
- GDPR compliance logging

## Limitations & Future Improvements

### Current Limitations
- No persistent database; data resets on app restart
- Single-instance deployment (no multi-user support)
- Limited error recovery for API failures
- No authentication or user verification

### Potential Improvements
- Add database integration for candidate storage
- Implement retry logic for API failures
- Add admin dashboard to review evaluations
- Deploy on cloud platform (AWS/GCP) for production use
- Add email notifications to candidates
- Implement role-based access control

## Deployment

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment (Future)
- AWS EC2 with Streamlit Server
- GCP Cloud Run with containerization (Docker)
- Heroku for quick prototyping

## Testing

To test the chatbot:

1. **Info Collection**: Provide incomplete information, verify follow-up prompts
2. **Question Generation**: Verify questions match declared tech stack
3. **Off-Topic Handling**: Try asking unrelated questions, verify redirection
4. **Edge Cases**: Try special characters, very long inputs, minimal responses

## Contributing

This is an assignment project. For improvements or bug reports, please document clearly with context.

## License

Internal use only.

## Contact & Support

For questions about the screening process, candidates should contact the HR team.
For technical issues or deployment help, refer to the documentation above.

---

**Last Updated**: December 2024
**Version**: 0.1.0
