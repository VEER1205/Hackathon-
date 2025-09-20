import google.generativeai as genai
from app.config import settings
from fastapi import APIRouter, HTTPException
import json
import re

# Configure Gemini client
genai.configure(api_key=settings.API_KEY)

router = APIRouter()


@router.get("/ask/")
async def ask_gemini(prompt: str):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  # safer choice
        response = model.generate_content(prompt)

        # Make sure response has text
        if not hasattr(response, "text"):
            raise HTTPException(status_code=500, detail="No text returned from Gemini")

        return {"response": response.text}

    except Exception as e:
        # Bubble up Gemini errors instead of plain 500
        raise HTTPException(status_code=500, detail=str(e))


# Assuming genai is a valid library for your generative model


@router.get("/question/")
async def question_gemini(age: int):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        Generate 15 psychometric test questions in valid JSON format for a person who is {age} years old.

        The response must meet the following:
        - Return only a valid JSON object.
        - The top-level key should be "questions".
        - Each item in "questions" must have the following fields: id, type, question, and options (if applicable).
        - Do NOT include any explanation, markdown (e.g. ```json), or surrounding text. Only return raw JSON.
        """

        response = model.generate_content(prompt)
        
        # New code to clean the response
        cleaned_text = re.search(r"\{.*\}", response.text, re.DOTALL)
        if not cleaned_text:
            raise HTTPException(status_code=500, detail="Could not find a valid JSON object in the model's response.")
        
        json_string = cleaned_text.group(0)

        try:
            json_data = json.loads(json_string)  # content must be a valid JSON string
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500, detail=f"Model returned invalid JSON: {e}"
            )

        return {"response": json_data}

    except Exception as e:
        # Bubble up Gemini errors instead of plain 500
        raise HTTPException(status_code=500, detail=str(e))