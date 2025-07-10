import uuid
from _collections_abc import Generator
from typing import cast

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from .service.chatbot import State, langgraph_app

LENGTH_THRES = 200

app = FastAPI()


# Input structure from frontend
class ChatRequest(BaseModel):
    messages: str
    language: str
    thread_id: str


@app.post("/chat/stream/")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    thread_id = req.thread_id or str(uuid.uuid4())
    state: State = {
        "messages": req.messages,
        "language": req.language,
    }
    config = cast("RunnableConfig", {"configurable": {"thread_id": thread_id}})

    def event_generator() -> Generator[str, None]:
        # Prevent timeout
        yield "event: ping\ndata: keepalive\n\n"
        for chunk, _ in langgraph_app.stream(state, config, stream_mode="messages"):
            if isinstance(chunk, AIMessage) and chunk.content:
                if len(chunk.content) > LENGTH_THRES:
                    continue
                yield f"event: chunk\ndata: {chunk.content}\n\n"
        yield f"event: {'end'}\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
