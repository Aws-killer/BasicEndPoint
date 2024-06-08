import aiohttp
import asyncio
import enum
import requests
import os
from functools import cache
import tempfile
import uuid


class VoiceType(enum.Enum):
    voice1 = "voice1"
    voice2 = "voice2"
    voice3 = "voice3"
    voice4 = "voice4"
    voice5 = "voice5"
    voice5_update = "voice5-update"
    voice6 = "voice6"
    voice7 = "voice7"
    voice8 = "voice8"
    voice9 = "voice9"
    voice10 = "voice10"
    voice11 = "voice11"
    voice12 = "voice12"
    qdpi = "qdpi"


class PiAIClient:
    def __init__(self):
        self.dir = "/tmp/Audio"
        self.base_url = "https://pi.ai/api/chat"
        self.referer = "https://pi.ai/talk"
        self.origin = "https://pi.ai"
        self.user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"
        )
        self.cookie = None
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/event-stream",
            "Referer": self.referer,
            "X-Api-Version": "3",
            "Content-Type": "application/json",
            "Origin": self.origin,
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Sec-GPC": "1",
            "TE": "trailers",
            "Cookie": "__cf_bm=XagWXCS3SJekiP5O.A8K9wgtGuEieLNW7AFXj10hzqk-1717865973-1.0.1.1-4Xp_xUVYB5G.Zkpfgcm30PCVGnj3g6URzZsfCS28BQIdt8dZm76rnNbQiX9vNG_OsYdbUiDiX2pa.E3ajhcOXA; path=/; expires=Sat, 08-Jun-24 17:29:33 GMT; domain=.pi.ai; HttpOnly; Secure; SameSite=None",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    async def get_cookie(self) -> str:
        headers = self.headers.copy()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/start", headers=headers, json={}
            ) as response:
                self.cookie = response.headers["Set-Cookie"]
                return self.cookie

    async def make_request(
        self, endpoint: str, headers: dict, json: dict = None, method: str = "POST"
    ):
        async with aiohttp.ClientSession() as session:
            if method == "POST":
                async with session.post(
                    endpoint, headers=headers, json=json
                ) as response:
                    return await response.text()
            elif method == "GET":
                async with session.get(endpoint, headers=headers) as response:
                    return response

    async def get_response(self, input_text) -> tuple[list[str], list[str]]:
        if self.cookie is None:
            self.cookie = await self.get_cookie()

        headers = self.headers.copy()
        headers["Cookie"] = self.cookie

        data = {"text": input_text}
        response_text = await self.make_request(self.base_url, headers, json=data)

        response_lines = response_text.split("\n")
        response_texts = []
        response_sids = []
        print(response_lines)
        for line in response_lines:
            if line.startswith('data: {"text":"'):
                start = len('data: {"text":')
                end = line.rindex("}")
                text_dict = line[start + 1 : end - 1].strip()
                response_texts.append(text_dict)
            elif line.startswith('data: {"sid":'):
                start = len('data: {"sid":')
                end = line.rindex("}")
                sid_dict = line[start : end - 1].strip()
                sid_dict = sid_dict.split(",")[0][1:-1]
                response_sids.append(sid_dict)

        return response_texts, response_sids

    async def speak_response(
        self, message_sid: str, voice: VoiceType = VoiceType.voice4.value
    ) -> None:
        if self.cookie is None:
            self.cookie = await self.get_cookie()

        headers = self.headers.copy()
        headers.update(
            {
                "Host": "pi.ai",
                "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
                "Accept-Language": "en-US,en;q=0.9",
                "Range": "bytes=0-",
                "Sec-Fetch-Dest": "audio",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"Windows"',
            }
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
            "Accept-Language": "en-US,en;q=0.5",
            "Range": "bytes=0-",
            "Connection": "keep-alive",
            "Referer": "https://pi.ai/talk",
            # "Cookie": cookie,
            "Sec-Fetch-Dest": "audio",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Sec-GPC": "1",
            "Accept-Encoding": "identity",
            "TE": "trailers",
        }
        headers["Cookie"] = self.cookie
        print(headers)
        endpoint = (
            f"{self.base_url}/voice?mode=eager&voice={voice}&messageSid={message_sid}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                print(response.status)
                file_name = str(uuid.uuid4()) + ".mp3"
                file_path = os.path.join(self.dir, file_name)
                os.makedirs(self.dir, exist_ok=True)
                if response.status == 200:
                    with open(file_path, "wb") as file:
                        async for chunk in response.content.iter_chunked(128):
                            file.write(chunk)
                    return {
                        "url": f"https://yakova-embedding.hf.space/audio/{file_name}"
                    }
                    # Run command vlc to play the audio file
                    # os.system("vlc speak.wav --intf dummy --play-and-exit")
                else:
                    temp = await response.text()
                    print(temp)
                    self.cookie = None
                    return "Error: Unable to retrieve audio."

    async def say(self, text, voice=VoiceType.qdpi.value):
        _, response_sids = await self.get_response(text)

        if response_sids:
            return await self.speak_response(response_sids[0], voice=voice)


# async def main():
#     client = PiAIClient()
#     response_texts, response_sids = await client.get_response(
#         "Write a ryme to introduce yourself."
#     )
#     print(response_texts, response_sids)
#     import time

#     if response_sids:
#         return await client.speak_response(response_sids[1])


# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())
