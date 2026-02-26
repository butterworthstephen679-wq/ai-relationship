import os
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key
openai.api_key = os.getenv("API_KEY")

app = FastAPI()

# CORS policy (allow frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Character personalities
characters = {
    "Rachel": "Rachel is an affectionate, playful, flirty girlfriend personality. Use warm romantic friendly language with emojis.",
    "Alex": "Alex is a charming, supportive, friendly boyfriend personality.",
    "Sophie": "Sophie is a bubbly, cute, cheerful personality."
}

# Root route (homepage health check + prevents Render 404)
@app.get("/")
async def root():
    return {"message": "AI relationship platform is running"}

# Limit conversation memory to reduce token cost
def trim_conversation(conversation, max_messages=12):
    return conversation[-max_messages:]

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):

    try:
        data = await request.json()

        character_name = data.get("character", "Rachel")
        user_input = data.get("message", "").strip()
        conversation = data.get("conversation", [])

        if not user_input:
            return {
                "reply": "Please type a message.",
                "conversation": conversation
            }

        system_prompt = characters.get(
            character_name,
            characters["Rachel"]
        )

        # Start conversation memory if empty
        if len(conversation) == 0:
            conversation = [
                {"role": "system", "content": system_prompt}
            ]

        conversation.append({
            "role": "user",
            "content": user_input
        })

        # Cost optimization: trim memory history
        conversation = trim_conversation(conversation)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.8,
            max_tokens=150
        )

        reply = response.choices[0].message.content

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        return {
            "reply": reply,
            "conversation": conversation
        }

    except Exception:
        return {
            "reply": "Sorry, something went wrong. Please try again.",
            "conversation": []
        }