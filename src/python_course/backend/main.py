import uuid
from _collections_abc import Generator
from typing import cast

import orjson
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from .service.chatbot import State, langgraph_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to Streamlit's local port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input structure from frontend
class ChatRequest(BaseModel):
    messages: str
    language: str
    thread_id: str


# Output structure
class ChatResponse(BaseModel):
    response: str
    thread_id: str


@app.post("/chat")
async def chat(req: ChatRequest) -> dict[str, str]:
    thread_id = req.thread_id or str(uuid.uuid4())
    state: State = {
        "messages": [HumanMessage(content=req.messages)],
        "language": req.language,
    }
    config = cast("RunnableConfig", {"configurable": {"thread_id": thread_id}})

    final_output = ""
    output = langgraph_app.invoke(state, config)  # type: ignore[arg-type]
    for message in output.get("messages", []):
        if isinstance(message, AIMessage):
            final_output = str(message.content)

    return {"response": final_output, "thread_id": thread_id}


@app.post("/chat/stream")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    thread_id = req.thread_id or str(uuid.uuid4())
    state: State = {
        "messages": req.messages,  # type: ignore[typeddict-item]
        "language": req.language,
    }
    config = cast("RunnableConfig", {"configurable": {"thread_id": thread_id}})

    def event_generator() -> Generator[str, None, None]:
        # Prevent timeout
        yield "event: ping\ndata: keepalive\n\n"
        for chunk, _ in langgraph_app.stream(state, config, stream_mode="messages"):  # type: ignore[arg-type]
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                data_str: str = orjson.dumps(obj=chunk.content).decode()
                yield f"event: chunk\ndata: {data_str}\n\n"
        yield f"event: {'end'}\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
