from fastapi import FastAPI, HTTPException
import aiohttp

from HuggingChat import getChatBot
import json
from pydantic import BaseModel
from Pi import handleSpeak


class Req(BaseModel):
    prompt: str
    llm: str = "CohereForAI/c4ai-command-r-plus"


class Speaker(BaseModel):
    text: str


app = FastAPI()


@app.post("/generate")
async def generate_message(request_body: Req):
    prompt = request_body.prompt
    huggingChat = getChatBot(request_body.llm)
    temp = str(huggingChat.query(prompt))
    temp = json.loads(temp.split("```json")[1].split("```")[0].strip())
    return temp


@app.post("/speak")
async def generate_speak(request_body: Speaker):
    prompt = request_body.text

    return await handleSpeak(prompt)
