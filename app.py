from fastapi import FastAPI, HTTPException, Request
import aiohttp, os

# from HuggingChat import getChatBot
import json
from pydantic import BaseModel
from Pi import PiAIClient
import aiofiles
from typing import List, Optional
from fastapi.responses import StreamingResponse, FileResponse

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


# @app.post("/generate")
# async def generate_message(request_body: Req):
#     prompt = request_body.prompt
#     huggingChat = getChatBot(request_body.llm)
#     temp = str(huggingChat.query(prompt))
#     temp = json.loads(temp.split("```json")[1].split("```")[0].strip())
#     return temp


@app.post("/speak")
async def pi_tts(req: PiTTSRequest):
    return await pi.say(text=req.text, voice=req.voice)


@app.get("/audio/{audio_name}")
async def serve_audio(request: Request, audio_name: str):
    audio_directory = "/tmp/Audio"
    audio_path = os.path.join(audio_directory, audio_name)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    range_header = request.headers.get("Range", None)
    audio_size = os.path.getsize(audio_path)

    if range_header:
        start, end = range_header.strip().split("=")[1].split("-")
        start = int(start)
        end = audio_size if end == "" else int(end)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{audio_size}",
            "Accept-Ranges": "bytes",
            # Optionally, you might want to force download by uncommenting the next line:
            # "Content-Disposition": f"attachment; filename={audio_name}",
        }

        content = read_file_range(audio_path, start, end)
        return StreamingResponse(content, media_type="audio/mpeg", headers=headers)

    return FileResponse(audio_path, media_type="audio/mpeg")


async def read_file_range(path, start, end):
    async with aiofiles.open(path, "rb") as file:
        await file.seek(start)
        while True:
            data = await file.read(1024 * 1024)  # read in chunks of 1MB
            if not data or await file.tell() > end:
                break
            yield data
