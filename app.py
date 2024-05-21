from fastapi import FastAPI, HTTPException
import aiohttp
from HuggingChat import chatbot as huggingChat
import json
from pydantic import BaseModel


class Req(BaseModel):
    prompt: str


app = FastAPI()


@app.post("/generate")
async def generate_message(request_body: Req):
    prompt = request_body.prompt

    temp = str(huggingChat.query(prompt))
    temp = json.loads(temp.split("```json")[1].split("```")[0].strip())
    return temp
