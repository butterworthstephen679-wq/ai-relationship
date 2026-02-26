import os
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API key
API_KEY = os.getenv("API_KEY")

# Character personalities
characters = {
    "Rachel": "Rachel is an affectionate, playful, flirty girlfriend personality. Respond warmly using romantic friendly language with emojis.",
    "Alex": "Alex is a charming supportive boyfriend personality.",
    "Sophie": "Sophie is a bubbly cheerful personality."
}

# Homepage route (serves frontend)
@app.get("/")
async def root():
    if not os.path.exists("index.html"):
        return HTMLResponse("<h1>Homepage not found</h1>")

    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Conversation memory trimming
def trim_conversation(conversation, max_messages=12):
    return conversation[-max_messages:]

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):

    try:
        if not API_KEY:
            return {"reply": "Server API key is missing.", "conversation": []}

        openai.api_key = API_KEY

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

        if len(conversation) == 0:
            conversation = [
                {"role": "system", "content": system_prompt}
            ]

        conversation.append({"role": "user", "content": user_input})

        conversation = trim_conversation(conversation)

        print("Calling OpenAI API...")

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.8,
            max_tokens=150
        )

        reply = response.choices[0].message.content

        conversation.append({"role": "assistant", "content": reply})

        return {
            "reply": reply,
            "conversation": conversation
        }

    except Exception as e:
        print("CHAT ERROR:", str(e))

        return {
            "reply": "Sorry, something went wrong.",
            "conversation": []
        }