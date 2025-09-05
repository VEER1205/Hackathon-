import google.generativeai as genai
from app.config import settings
from fastapi import APIRouter, HTTPException

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
