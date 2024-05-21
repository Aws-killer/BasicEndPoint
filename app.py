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
    message = str(huggingChat.query(prompt))

    return message
