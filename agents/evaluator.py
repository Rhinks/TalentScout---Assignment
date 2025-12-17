# Answer Evaluator Agent logic

from openai import OpenAI
import os
import dotenv
from pydantic import BaseModel
from typing import List

class EvaluationResult(BaseModel):
    score: int                 #0 - 10
    verdict: str               #"PASS" | "BORDERLINE" | "FAIL"
    summary: str               #short explanation
    strengths: List[str]
    weaknesses: List[str]

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def assessment_agent(candidate_data, questions, answers):

    qa_pairs = [
        {
            "question": q,
            "answer": answers.get(q, "")
        }
        for q in questions
    ]

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {
                "role": "system",
                "content": f"""
                        You are a technical evaluator for an initial hiring screening.

                        Candidate context:
                        - Role: {candidate_data.get("desired_positions")}
                        - Years of experience: {candidate_data.get("yoe")}
                        - Tech stack: {candidate_data.get("tech_stack")}

                        You are given technical questions and the candidate's answers.

                        Evaluation rules:
                        - Judge correctness, clarity, and technical accuracy
                        - Partial answers are acceptable
                        - Do NOT be overly strict
                        - Focus on whether the candidate likely has real hands-on experience

                        Scoring rubric:
                        - 0–3: Mostly incorrect or vague answers
                        - 4–6: Some correct understanding, but gaps
                        - 7–8: Mostly correct, practical knowledge
                        - 9–10: Strong, confident, accurate answers

                         Note: If answer is 'pass', 'idk', or 'I don't know', treat as incorrect (score 0 for that question).

                        Verdict rules:
                        - PASS → score ≥ 7
                        - BORDERLINE → score 4–6
                        - FAIL → score ≤ 3

                        Output rules:
                        - Be concise and professional
                        - Do not mention the rubric explicitly
                        - Base judgment strictly on provided answers
                        """
            },
            {
                "role": "user",
                "content": f"""
                    Here are the questions and answers:
                    {qa_pairs}
                    """
            }
        ],
        text_format=EvaluationResult
    )

    return response.output_parsed.model_dump()

