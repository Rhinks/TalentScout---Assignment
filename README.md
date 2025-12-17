# TalentScout - Hiring Screening Chatbot

## Project Overview

TalentScout is a technical screening chatbot built to streamline the initial hiring process. It automates candidate information collection and technical assessment through a conversational interface powered by OpenAI's GPT-4o-2024-08-06 model.

The chatbot:
- Gathers candidate information (name, email, phone, experience, desired roles, location, tech stack)
- Generates tailored technical questions based on declared skills and experience level
- Evaluates candidate responses with scoring and feedback
- Provides graceful completion messaging
- Displays candidate details in a sidebar during screening

This is designed for small to medium-scale recruitment processes where initial technical screening needs to be efficient and consistent.

## Features

- **Information Collection**: Gathers candidate details through natural conversation with LLM-powered extraction
- **Adaptive Questions**: Generates 3-5 technical questions based on candidate's tech stack and years of experience (junior/mid/senior difficulty)
- **Technical Assessment**: Evaluates answers for correctness, clarity, and evidence of practical experience (0-10 scoring scale)
- **User-Friendly Interface**: Dark-themed chat interface via Streamlit with real-time candidate details in sidebar
- **Graceful Exit**: Users can end screening at any point via "End Interview" button
- **Off-Topic Handling**: Redirects candidates back to screening scope if questions are unrelated
- **Session State Management**: Full message history persistence across reruns
- **Loading States**: Spinners and delays for better UX during processing

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
    OPENAI_API_KEY=your_openai_api_key_here
    ```

4. **Run the application**
    ```bash
    streamlit run streamlit_app.py
    ```

The chatbot will be accessible at `http://localhost:8501`

## Usage Guide

### Starting the Screening
1. Open the Streamlit app
2. Read the welcome greeting and process overview
3. Provide your full name when prompted

### Information Collection Phase
- Answer questions about email, phone, years of experience, desired roles, current location, and technology stack
- The chatbot will ask for missing information until all required fields are complete
- Information is extracted and validated in real-time using LLM
- Sidebar updates to show collected name and email

### Technical Questions Phase
- After information collection completes, you'll receive instructions
- 5-second preparation time while personalized questions are generated
- You'll receive 3-5 technical questions tailored to your declared tech stack and experience level
- Answer each question clearly and concisely
- Brief loading delay (1.5 seconds) between questions for better readability
- Questions automatically advance to assessment phase after all responses are submitted

### Screening Completion
- After answering all questions, your responses are automatically evaluated
- You'll receive a completion message with information about next steps
- The input field is disabled to prevent further responses
- Session details displayed in sidebar

### Early Exit
- Click the "End Interview" button in the sidebar to end the conversation at any time

## Technical Details

### Architecture

The system follows a modular agent-based architecture with orchestration:

```
streamlit_app.py (UI/State Management/Chat Interface)
    ↓
orchestrator.py (Flow Control & Stage Management)
    ├── agents/info_collector.py (Information extraction agent)
    ├── agents/question_generator.py (Adaptive question generation agent)
    └── agents/evaluator.py (Response evaluation & scoring agent)
```

### Screening Stages

1. **INFO_COLLECTION**: Gathers candidate data through conversation
2. **QUESTION_GENERATION**: Generates personalized technical questions based on profile
3. **ASK_QUESTIONS**: Presents questions sequentially and collects answers
4. **ASSESSMENT**: Evaluates responses and generates scores/verdicts
5. **CONVO_END**: Concludes screening with final messaging

### Technology Stack

- **Frontend**: Streamlit 1.x with custom dark theme CSS
- **LLM**: OpenAI GPT-4o-2024-08-06 with structured output parsing
- **Language**: Python 3.12
- **Data Validation**: Pydantic models
- **Package Manager**: uv
- **Environment Management**: python-dotenv

### Key Files

- `streamlit_app.py`: Main Streamlit application, UI layout, session state initialization, chat interface
- `orchestrator.py`: Core orchestration logic managing stage transitions and agent routing
- `agents/info_collector.py`: Extracts structured candidate information using LLM
- `agents/question_generator.py`: Generates adaptive technical questions (3-5 per candidate)
- `agents/evaluator.py`: Evaluates candidate responses and provides scores (0-10), verdicts (PASS/BORDERLINE/FAIL), strengths, and weaknesses
- `requirements.txt`: Python dependencies for deployment
- `.env`: API keys and configuration (not tracked in git)

### Data Flow

1. User input is received in chat interface
2. Orchestrator determines current stage
3. Appropriate agent is called with current state and user input
4. LLM response is parsed using Pydantic models
5. Extracted data or response is validated
6. Session state is updated with new information
7. Response message is displayed to user and appended to message history
8. On stage transitions, orchestrator falls through to next stage without requiring additional user input

### LLM Integration

All agents use OpenAI's structured output parsing feature:
- **Info Collector**: Extracts fields into `Info` Pydantic model
- **Question Generator**: Outputs list of questions as `TechQuestions` model
- **Evaluator**: Returns structured `EvaluationResult` with score, verdict, summary, strengths, and weaknesses

## Prompt Design

### Information Collection Prompt

The info_collector agent is instructed to:
- Extract only explicitly provided information
- Avoid guessing or inferring missing details
- Redirect off-topic questions politely back to the screening
- Return only newly extracted fields (omit fields not mentioned)
- Handle special characters and various input formats

This ensures data accuracy and prevents hallucination.

### Question Generation Prompt

The question_generator agent uses:
- **Adaptive Difficulty Matrix**: Adjusts question complexity based on years of experience
  - 0-2 years: Basic syntax, API usage, standard library
  - 3-5 years: Common pitfalls, debugging, framework specifics
  - 5+ years: Performance, internals, memory management, security
- **Question Constraints**: 
  - Maximum 20 words per question
  - Specific function names, decorators, or CLI commands
  - Binary/factual answers preferred over open-ended opinions
  - No "What is X?" style questions
- **Tech Stack Focus**: Questions strictly based on declared technologies
- **No Code Snippets**: Questions are answerable in 1-2 short sentences

Example: For a Python Junior with FastAPI, questions focus on list methods, async/await basics, FastAPI dependency injection, etc.

### Evaluation Prompt

The evaluator assesses answers based on:
- Correctness and technical accuracy
- Clarity of explanation
- Evidence of practical hands-on experience
- Partial answers are acceptable
- Not overly strict grading

**Scoring Rubric**:
- 0–3: Mostly incorrect or vague answers
- 4–6: Some correct understanding, but gaps
- 7–8: Mostly correct, practical knowledge
- 9–10: Strong, confident, accurate answers

**Verdict Rules**:
- PASS → score ≥ 7
- BORDERLINE → score 4–6
- FAIL → score ≤ 3

## Challenges & Solutions

### Challenge 1: Multi-turn Context
**Problem**: Initial implementation treated each turn independently, losing context.
**Solution**: Maintain full message history in `st.session_state` and pass to agents. This allows coherent follow-up questions and better information gathering.

### Challenge 2: Stage Transitions Without User Input
**Problem**: After info collection completes, chatbot required user input before moving to question generation.
**Solution**: Implement fall-through logic in orchestrator—when a stage changes, continue processing the new stage in the same function call instead of returning early.

### Challenge 3: Message Persistence on Rerun
**Problem**: Instructions and questions disappeared on Streamlit rerun when using `st.write()`.
**Solution**: Add messages to `st.session_state.messages` directly so they persist in message history across reruns.

### Challenge 4: LLM Output Validation
**Problem**: LLM sometimes returned partial or invalid JSON structures.
**Solution**: Used Pydantic models with Optional fields and `exclude_none=True` to handle partial data gracefully.

### Challenge 5: Question Generation Flow
**Problem**: Instructions showed but required extra user input before questions appeared.
**Solution**: Return instructions and first question in single response after 5-second spinner, allowing natural reading time while questions generate.

### Challenge 6: Data Privacy
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
- No export functionality for evaluation results

### Potential Improvements
- Add PostgreSQL/MongoDB integration for candidate storage
- Implement retry logic for API failures with exponential backoff
- Add admin dashboard to review evaluations and candidate profiles
- Deploy on cloud platform (AWS/GCP) for production use
- Add email notifications to candidates with evaluation results
- Implement role-based access control for admin panel
- Add candidate resume parsing for enriched assessment
- Support multiple languages
- Add video interview recording integration

## Deployment

### Local Deployment
```bash
streamlit run streamlit_app.py
```

### Hugging Face Spaces Deployment
The application is deployed on Hugging Face Spaces at: **https://huggingface.co/spaces/Rhinks/TalentScout**

#### Setup Steps:
1. Create a Hugging Face Space with Streamlit runtime
2. Push code to Space repo:
   ```bash
   git clone https://huggingface.co/spaces/{username}/{space-name}
   cp streamlit_app.py orchestrator.py requirements.txt agents/ to cloned repo
   git push
   ```
3. Add API key in Space **Settings** → **Repository secrets**:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
4. Space auto-deploys and runs at the provided URL

Note: Rename `app.py` to `streamlit_app.py` for HF Spaces auto-detection.

### Cloud Deployment (Future)
- AWS EC2 with Streamlit Server
- GCP Cloud Run with containerization (Docker)
- Heroku for quick prototyping

## Testing

To test the chatbot:

1. **Info Collection**: 
   - Provide incomplete information, verify follow-up prompts
   - Test with various formats (e.g., phone numbers, email formats)
   - Verify sidebar updates with collected data

2. **Question Generation**: 
   - Verify questions match declared tech stack
   - Test with different experience levels (junior/mid/senior)
   - Verify 5-second spinner appears

3. **Off-Topic Handling**: 
   - Try asking unrelated questions during info collection
   - Verify polite redirection to screening

4. **Edge Cases**: 
   - Try special characters, very long inputs, minimal responses
   - Test exit button at different stages
   - Verify message history persists correctly

## Code Attribution

**AI-Assisted Development**: Portions of this project, including comprehensive docstrings, README documentation, and system prompt engineering, were developed with assistance from AI language models (Claude/GPT). All functionality has been reviewed and validated for correctness and adherence to requirements.

## Contributing

This is an assignment project. For improvements or bug reports, please document clearly with context.

## License

Internal use only.

## Contact & Support

For questions about the screening process, candidates should contact the HR team.
For technical issues or deployment help, refer to the documentation above.

---

**Last Updated**: December 17, 2024
**Version**: 0.1.0
**Python Version**: 3.12+
**Status**: Functional, Deployed on HF Spaces
**Live Demo**: https://huggingface.co/spaces/Rhinks/TalentScout
