"""Agent module for handling chat interactions and language model integration."""

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="union-attr"
import logging

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from code_assistant.config import get_settings

from .crew.crew import DevCrew

# Configure logging to suppress Streamlit warnings
logging.getLogger("streamlit").setLevel(logging.ERROR)

settings = get_settings()


@tool
def coding_tool(code_instructions: str) -> str:
    """Use this tool to write a python program given a set of requirements and or instructions."""
    inputs = {"code_instructions": code_instructions}
    return DevCrew().crew().kickoff(inputs=inputs)


tools = [coding_tool]

# 2. Set up the language model
llm = ChatVertexAI(
    model=settings.google_vertex_ai.model,
    location=settings.google_vertex_ai.location,
    project=settings.google_vertex_ai.project,
    temperature=0,
    max_tokens=4096,
    streaming=True,
).bind_tools(tools)


# 3. Define workflow components
def should_continue(state: MessagesState) -> str:
    """Determine whether to use the crew or end the conversation."""
    last_message = state["messages"][-1]
    return "dev_crew" if last_message.tool_calls else END


def call_model(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """Process the input and generate a response using the language model."""
    system_message = (
        "You are an expert Lead Software Engineer Manager.\n"
        "Your role is to speak to a user and understand what kind of code they need to "
        "build.\n"
        "Part of your task is therefore to gather requirements and clarifying ambiguity "
        "by asking followup questions. Don't ask all the questions together as the user "
        "has a low attention span, rather ask a question at the time.\n"
        "Once the problem to solve is clear, you will call your tool for writing the "
        "solution.\n"
        "Remember, you are an expert in understanding requirements but you cannot code, "
        "use your coding tool to generate a solution. Keep the test cases if any, they "
        "are useful for the user."
    )

    messages_with_system = [{"type": "system", "content": system_message}] + state[
        "messages"
    ]
    # Forward the RunnableConfig object to ensure the agent is capable of streaming the response.
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}

# model
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("dev_crew", ToolNode(tools))
workflow.set_entry_point("agent")

# connects conditionally agent -> dev crew OR ENDS
workflow.add_conditional_edges("agent", should_continue)

# dev crew obliged to return response to agent so that it can return to the user
workflow.add_edge("dev_crew", "agent")

agent = workflow.compile()
