# %%
import getpass
import os

# %%
from collections.abc import Sequence
from typing import Annotated

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# %%
load_dotenv()
api_key_l = os.getenv("LANG_SMITH_API_KEY")
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


# Define a new graph
workflow = StateGraph(state_schema=State)

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

# %%
trimmer = trim_messages(
    max_tokens=500,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)


# Define to call the model
def call_model(state: State) -> dict[str, BaseMessage]:
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(
        {"messages": trimmed_messages, "language": state["language"]}
    )
    response = model.invoke(prompt)
    return {"messages": response}


# %%
# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# %%
# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# %%
config = {"configurable": {"thread_id": "abc123"}}

# %%
query = "Hi! I'm Dog. Write me a self introduction with 100 words."
language = "English"

input_messages = [HumanMessage(query)]
for chunk, _ in app.stream(
    {"messages": input_messages, "language": language},
    config=config,
    stream_mode="messages",
):
    if isinstance(chunk, AIMessage):  # Filter to just model responses
        print(chunk.content, end="|")  # noqa: T201

# %%
query = "Who am I?"

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "language": language},
    config=config,
)
output["messages"][-1].pretty_print()
