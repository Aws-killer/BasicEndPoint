from fastapi import FastAPI, HTTPException
import aiohttp

from HuggingChat import getChatBot
import json
from pydantic import BaseModel
from Pi import PiAIClient
import aiofiles
from typing import List, Optional

pi = PiAIClient()


class Req(BaseModel):
    prompt: str
    llm: str = "CohereForAI/c4ai-command-r-plus"


class PiTTSRequest(BaseModel):
    text: str
    voice: Optional[str]


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
async def pi_tts(req: PiTTSRequest):
    return await pi.say(text=req.text, voice=req.voice)
