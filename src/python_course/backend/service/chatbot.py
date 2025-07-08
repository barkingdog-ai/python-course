# %%
import getpass
import os
import typing

# %%
from collections.abc import Sequence
from typing import Annotated

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# %%
load_dotenv()
api_key_l = os.getenv("LANG_SMITH_API_KEY")
if api_key_l is None:
    raise ValueError("LANGSMITH_API_KEY is not set")
# %%
if not os.environ.get("LANG_SMITH_API_KEY"):
    os.environ["LANG_SMITH_API_KEY"] = getpass.getpass()

# %%
# connect langsmith
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = api_key_l
# %%
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# %%
# set the GOOGLE_KEY environment
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass()


# %%
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


# %%
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str


# %%
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def get_trimmed_history(state: State) -> list[BaseMessage]:
    trimmer = trim_messages(
        max_tokens=500,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )
    result = trimmer.invoke(state["messages"])
    return typing.cast("list[BaseMessage]", result)


def generate_response(
    messages: list[BaseMessage], language: str, config: RunnableConfig
) -> AIMessage:
    prompt = prompt_template.invoke({"messages": messages, "language": language})
    result = model.invoke(prompt, config)
    return AIMessage(content=result.content)


# Define to call the model
def call_model(state: State, config: RunnableConfig) -> dict[str, list[BaseMessage]]:
    trimmed_messages = get_trimmed_history(state)

    ai_msg = generate_response(trimmed_messages, state["language"], config)
    return {"messages": [*state["messages"], ai_msg]}
