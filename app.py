import os
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Character personalities (shorter prompts = cheaper and faster)
characters = {
    "Rachel": "Rachel is an affectionate, playful, flirty girlfriend personality. Respond warmly using light romantic and friendly language with emojis.",
    "Alex": "Alex is a charming, supportive, friendly boyfriend personality.",
    "Sophie": "Sophie is a bubbly, cute, cheerful, positive personality."
}

# Limit memory context to reduce token cost
def trim_conversation(conversation, max_messages=12):
    return conversation[-max_messages:]

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()

        character_name = data.get("character", "Rachel")
        user_input = data.get("message", "").strip()
        conversation = data.get("conversation", [])

        if not user_input:
            return {"reply": "Please type a message.", "conversation": conversation}

        system_prompt = characters.get(
            character_name,
            characters["Rachel"]
        )

        # Start conversation if empty
        if len(conversation) == 0:
            conversation = [{"role": "system", "content": system_prompt}]

        conversation.append({"role": "user", "content": user_input})

        # Cost optimization: trim history
        conversation = trim_conversation(conversation)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.8,   # More natural personality responses
            max_tokens=150      # Controls cost + response length
        )

        reply = response.choices[0].message.content

        conversation.append({"role": "assistant", "content": reply})

        return {
            "reply": reply,
            "conversation": conversation
        }

    except Exception:
        return {
            "reply": "Sorry, I couldn't process that message.",
            "conversation": []
        }