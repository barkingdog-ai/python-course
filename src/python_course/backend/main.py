import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from .service.chatbot import langgraph_app

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
def chat(req: ChatRequest) -> dict[str, str]:
    thread_id = req.thread_id or str(uuid.uuid4())
    state = {
        "messages": [HumanMessage(content=req.message)],
        "language": req.language,
    }
    config = {"configurable": {"thread_id": thread_id}}

    final_output = ""
    for output, _ in langgraph_app.stream(state, config=config, stream_mode="messages"):
        messages = output.get("messages", [])
        for msg in messages:
            if isinstance(msg, AIMessage):
                final_output += str(msg.content)

    return {"response": final_output, "thread_id": thread_id}
