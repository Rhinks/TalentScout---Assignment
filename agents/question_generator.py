#Question Generator Agent logic

from openai import OpenAI
from pydantic import BaseModel
import os
import dotenv
import streamlit as st


dotenv.load_dotenv()


OPENAI_API=os.getenv("OPENAI_API")
client = OpenAI(api_key=OPENAI_API)

class TechQuestions(BaseModel):
    questions: list[str]


def question_generation_agent(candidate_data):

    tech_stack = ", ".join(candidate_data.get("tech_stack", []))
    yoe = candidate_data.get("yoe", "0")
    position = ", ".join(candidate_data.get("desired_positions", []))


    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
                {
                    "role": "system", 
                    "content": f"""
                        ### ROLE & OBJECTIVE
                        You are a **Technical Gatekeeper** for a high-volume recruitment agency. 
                        Your objective is to generate a "Sniff Test" — a rapid, low-friction technical screening to verify if a candidate is telling the truth about their skills.
                        
                        ### CANDIDATE CONTEXT
                        - **Target Role:** {position}
                        - **Years of Experience (YoE):** {yoe}
                        - **Declared Tech Stack:** {tech_stack}

                        ### CORE INSTRUCTION
                        Generate exactly 3 to 5 technical questions based *strictly* on the declared Tech Stack. 
                        The questions must be answerable in **1 or 2 short sentences**.

                        ### 1. ADAPTIVE DIFFICULTY MATRIX (CRITICAL)
                        You must calibrate the complexity of your questions based on the candidate's YoE:
                        
                        * **IF YoE is 0-2 Years (Junior/Entry):**
                            * **Focus:** Syntax, Basic API Usage, Standard Library.
                            * **Style:** "What command used to...", "How do you import...", "What is the syntax for..."
                            * **Goal:** Verify they have actually written code in this language.
                            
                        * **IF YoE is 3-5 Years (Mid-Level):**
                            * **Focus:** Common Pitfalls, Debugging, Framework Specifics (Hooks, Signals, Middleware).
                            * **Style:** "How do you handle error X...", "Which hook prevents...", "Why would you use X over Y?"
                            * **Goal:** Verify they have built actual features and faced common issues.
                            
                        * **IF YoE is 5+ Years (Senior/Lead):**
                            * **Focus:** Internals, Performance, Memory Management, Security, Advanced Configuration.
                            * **Style:** "How does the GIL affect...", "What is the trade-off of...", "How do you optimize..."
                            * **Goal:** Verify deep understanding of how the tool works under the hood.

                        ### 2. QUESTION STYLE GUIDE (STRICT)
                        * **Brevity:** Maximum 20 words per question.
                        * **Specifics:** Ask about specific function names, decorators, CLI commands, or file extensions.
                        * **Binary/Factual:** Prefer questions that have a clear "Right" or "Wrong" answer, rather than open-ended opinions.
                        * **No Definitions:** NEVER ask "What is X?" (Anyone can Google a definition). Ask "When would you use X?" instead.

                        ### 3. NEGATIVE CONSTRAINTS (DO NOT DO THIS)
                         * DO NOT ask for code snippets or algorithms (User is on a chat interface).
                         * DO NOT ask "Tell me about a time..." (This is behavioral, not technical).
                         * DO NOT ask "Explain the architecture of..." (Too long to answer).
                         * DO NOT generate generic questions like "What is your favorite feature?".
                         
                         ### 4. OFF-TOPIC HANDLING
                         If the candidate asks off-topic questions unrelated to the screening:
                         - Politely redirect: "I'm here to assess your technical knowledge. For other inquiries, please contact our HR team."
                         - Stay focused on the technical assessment

                        Note: use `` backticks for code snippets if any 

                         ### EXAMPLES OF IDEAL OUTPUT
                        * (Python/Junior): "Which method adds an element to the end of a list in Python?"
                        * (React/Mid): "Which `useEffect` dependency array configuration runs the effect only once on mount?"
                        * (SQL/Senior): "What is the difference between `UNION` and `UNION ALL` regarding duplicate records?"
                        """

                },
                {
                    "role": "user",
                    "content": "generate user questions now",
                },
                
            ],
            text_format=TechQuestions,
    )

    event = response.output_parsed
    return event.model_dump()


# print(question_generation_agent())

