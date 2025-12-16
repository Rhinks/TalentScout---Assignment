#Greeting + Information Collector Agent logic
from pydantic import BaseModel
from openai import OpenAI
import os
import dotenv
import streamlit as st
from typing import Optional

dotenv.load_dotenv()

class Info(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[int] = None
    yoe: Optional[int] = None
    desired_positions: Optional[list[str]] = None
    loc: Optional[str] = None
    tech_stack: Optional[list[str]] = None

OPENAI_API=os.getenv("OPENAI_API")
client = OpenAI(api_key=OPENAI_API)

def info_collection_agent(user_input:str, candidate_data):
    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {
                "role": "system", 
                "content": f"""
                    You are an information extraction agent in a hiring screening system.

                    Current candidate data (already collected):
                    {candidate_data}

                    Your task:
                    - Read the user's message
                    - Extract ONLY the information that is explicitly provided
                    - Return ONLY newly extracted fields (omit fields not mentioned)
                    - Do NOT guess or infer missing information
                    - Do NOT ask questions or provide explanations

                    Fields to extract:
                    - name (string)
                    - email (string)
                    - phone (integer, digits only)
                    - yoe (years of experience, integer)
                    - desired_positions (list of strings)
                    - loc (current location)
                    - tech_stack (list of technologies)

                    Output rules:
                    - Return ONLY a valid JSON object with extracted fields
                    - Include only fields present in the user's message
                    - No explanations, comments, or extra text
                    """
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        text_format=Info,
    )

    event = response.output_parsed
    return event.model_dump(exclude_none=True)

# info_collection_agent("hi, I'm rushbh mistry, from delhi", {})
