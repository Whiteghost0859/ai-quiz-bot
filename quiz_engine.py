import os
import json
import time
from groq import Groq  

# Initialize the free Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# open-source model
model = "llama-3.3-70b-versatile"

def generate_quiz_question_json(text, max_retries=3):
    """Generates a structured quiz question using a free Groq LLM."""
    system_prompt = """
    You are a quiz bot acting as an educational teacher's assistant. 
    Your task is to generate multiple-choice questions from the educational text provided by the user. 
    Each response must be returned as a single, valid JSON object following the requested schema.
    """
    
    user_prompt = f"""
    Generate a multiple-choice question based on the following educational text. 
    Return your response strictly as a JSON object with the following keys:
    - "question": The text of the question.
    - "options": A dictionary containing four choices with keys "A", "B", "C", and "D".
    - "answer": The single letter string representing the correct option (e.g., "A").

    Educational Text:
    {text}
    """

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},  # Keeps JSON output strict
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                timeout=15 
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e