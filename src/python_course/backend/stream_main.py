import asyncio
import os
from _collections_abc import AsyncGenerator

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


class Message(BaseModel):
    message: str


@app.post("/chat/stream/")
async def chat_stream(message: Message, request: Request) -> StreamingResponse:
    chat_session = model.start_chat()

    async def event_generator() -> AsyncGenerator[str, None]:
        res_str = chat_session.send_message(message.message, stream=True)
        for chunk in res_str:
            if await request.is_disconnected():
                print("Disconnected")  # noqa: T201
                break
            if chunk.text:
                data = f"data: {chunk.text}\n\n"
                yield data
                await asyncio.sleep(0.1)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
