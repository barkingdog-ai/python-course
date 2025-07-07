import uuid
from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
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
    message: str
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
        "messages": [HumanMessage(content=req.message)],
        "language": req.language,
    }
    config = cast("RunnableConfig", {"configurable": {"thread_id": thread_id}})

    final_output = ""
    output = langgraph_app.invoke(state, config)
    for message in output.get("messages", []):
        if isinstance(message, AIMessage):
            final_output = str(message.content)

    return {"response": final_output, "thread_id": thread_id}
