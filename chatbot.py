from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test mode AI characters
characters = {
    "Rachel": {
        "system": "You are Rachel, an affectionate, playful AI girlfriend for testing. Use nicknames and emojis. Keep it light and fun."
    },
    "Alex": {
        "system": "You are Alex, a charming and supportive AI boyfriend for testing. Be playful and positive."
    },
    "Sophie": {
        "system": "You are Sophie, a bubbly AI girlfriend for testing. Keep it cheerful and friendly."
    }
}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    character_name = data.get("character")
    user_input = data.get("message")
    conversation = data.get("conversation", [])

    # If conversation empty, add system message
    if not conversation:
        conversation = [{"role": "system", "content": characters[character_name]["system"]}]
    
    conversation.append({"role": "user", "content": user_input})

    # Test mode: simulate AI with static replies (to save tokens)
    if os.getenv("TEST_MODE", "true").lower() == "true":
        reply = f"(Test Mode) {character_name} says: I got your message '{user_input}' 💖"
        conversation.append({"role": "assistant", "content": reply})
        return {"reply": reply, "conversation": conversation}

    # Normal OpenAI call if TEST_MODE=false
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})

    return {"reply": reply, "conversation": conversation}