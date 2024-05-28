import asyncio
import os
import enum
import requests
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

import functools


def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return wrapper


class VoiceType(enum.Enum):
    voice1 = ("voice1",)
    voice2 = ("voice2",)
    voice3 = ("voice3",)
    voice4 = ("voice4",)
    voice5 = ("voice5",)
    voice5_update = ("voice5-update",)
    voice6 = ("voice6",)
    voice7 = ("voice7",)
    voice8 = ("voice8",)
    voice9 = ("voice9",)
    voice10 = ("voice10",)
    voice11 = ("voice11",)
    voice12 = ("voice12",)
    qdpi = ("qdpi",)


class PiAIClient:
    def __init__(self):
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
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    @memoize
    async def get_cookie(self, context: BrowserContext) -> str:
        headers = self.headers.copy()
        page = await context.new_page()
        response = await page.request.post(
            f"{self.base_url}/start", headers=headers, data={}
        )
        self.cookie = response.headers["set-cookie"]
        await page.close()
        return self.cookie

    async def make_request(
        self,
        context: BrowserContext,
        endpoint: str,
        headers: dict,
        json: dict = None,
        method: str = "POST",
    ):
        page = await context.new_page()
        if method == "POST":
            response = await page.request.post(endpoint, headers=headers, data=json)
        elif method == "GET":
            response = await page.request.get(endpoint, headers=headers)
        await page.close()
        return await response.text()

    async def get_response(
        self, context: BrowserContext, input_text
    ) -> tuple[list[str], list[str]]:
        if self.cookie is None:
            self.cookie = await self.get_cookie(context)

        headers = self.headers.copy()
        headers["Cookie"] = self.cookie

        data = {"text": input_text}
        response_text = await self.make_request(
            context, self.base_url, headers, json=data
        )

        response_lines = response_text.split("\n")
        response_texts = []
        response_sids = []
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
        self,
        context: BrowserContext,
        message_sid: str,
        voice: VoiceType = VoiceType.voice4,
    ) -> None:
        if self.cookie is None:
            self.cookie = await self.get_cookie(context)

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
            "Accept-Language": "en-US,en;q=0.5",
            "Range": "bytes=0-",
            "Connection": "keep-alive",
            "Referer": "https://pi.ai/talk",
            "Cookie": self.cookie,
            "Sec-Fetch-Dest": "audio",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Sec-GPC": "1",
            "Accept-Encoding": "identity",
            "TE": "trailers",
        }
        endpoint = f"{self.base_url}/voice?mode=eager&voice={voice.value}&messageSid={message_sid}"
        page = await context.new_page()
        response = await page.request.get(endpoint, headers=headers)
        if response.status == 200:
            with open("speak.wav", "wb") as file:
                async for chunk in response.body():
                    file.write(chunk)

            # Run command vlc to play the audio file
            os.system("vlc speak.wav --intf dummy --play-and-exit")
        else:
            print("Error: Unable to retrieve audio.")
        await page.close()

    async def trigger_event(self, context: BrowserContext):
        if self.cookie is None:
            self.cookie = await self.get_cookie(context)

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "text/plain",
            "cookie": self.cookie,
            "origin": "https://pi.ai",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://pi.ai/talk",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }
        data = {
            "n": "voice:audio-on",
            "u": "https://pi.ai/talk",
            "d": "pi.ai",
            "r": None,
        }

        endpoint = "https://pi.ai/proxy/api/event"
        response_text = await self.make_request(
            context, endpoint, headers, json=data, method="POST"
        )
        print(response_text)


async def handleSpeak(text):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        client = PiAIClient()
        response_texts, response_sids = await client.get_response(context, text)
        print(response_texts, response_sids)
        await client.trigger_event(context)
        if response_sids:
            await client.speak_response(context, response_sids[0])
        await browser.close()


# # To run the handleSpeak function:
# asyncio.run(handleSpeak("Hello, how are you?"))
