"""Streamlit application for the Code Assistant chat interface."""

import contextlib
import datetime
from io import StringIO
import json
from typing import Any

import streamlit as st

from code_assistant.app.agent import agent
from code_assistant.config import get_settings

# Load settings
settings = get_settings()


def safe_json_serialize(obj: Any) -> str:
    """Safely serialize an object to JSON, handling complex objects that can't be serialized."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except (TypeError, ValueError) as e:
        # If direct serialization fails, try to extract serializable parts
        try:
            if hasattr(obj, '__dict__'):
                simplified = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v 
                            for k, v in obj.__dict__.items()}
                return json.dumps(simplified, indent=2, default=str)
            else:
                return json.dumps({"error": f"Unable to serialize object: {str(e)}", "type": str(type(obj)), "value": str(obj)}, indent=2)
        except Exception as fallback_error:
            return json.dumps({"error": f"Serialization failed: {str(fallback_error)}", "original_error": str(e), "type": str(type(obj))}, indent=2)

# Configure page
st.set_page_config(
    page_title="Code Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_inputs" not in st.session_state:
    st.session_state.agent_inputs = []
if "agent_responses" not in st.session_state:
    st.session_state.agent_responses = []
if "interactions" not in st.session_state:
    st.session_state.interactions = []
if "terminal_output" not in st.session_state:
    st.session_state.terminal_output = []

# Custom CSS for the chat interface
st.markdown(
    """
    <style>
        /* Hide the default Streamlit footer */
        footer {display: none !important;}
        /* Add padding to the bottom of the chat container for the input box */
        .main > div {
            padding-bottom: 80px;
        }
        /* Style for the input container */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 70%;
            padding: 20px;
            background-color: white;
            border-top: 1px solid #ddd;
            z-index: 100;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Create two columns: main chat and debug panel
chat_col, debug_col = st.columns([0.7, 0.3])

with chat_col:
    st.title("💻 Code Assistant")

    # Display chat messages from history on app rerun
    message_container = st.container()
    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Create the input box at the bottom
    input_container = st.container()
    with input_container:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        prompt = st.chat_input("What would you like me to help you with?")
        st.markdown("</div>", unsafe_allow_html=True)

    if prompt:
        timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        interaction = {
            "timestamp": timestamp,
            "user_message": {"role": "user", "content": prompt},
            "assistant_message": None,
            "agent_input": None,
        }

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with message_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                response_container = st.empty()
                spinner = st.empty()

                # Capture terminal output
                stdout = StringIO()
                with (
                    contextlib.redirect_stdout(stdout),
                    contextlib.redirect_stderr(stdout),
                ):
                    # Convert chat history to agent message format
                    agent_messages = []
                    for msg in st.session_state.messages:
                        msg_type = "human" if msg["role"] == "user" else "ai"
                        agent_messages.append(
                            {"type": msg_type, "content": msg["content"]},
                        )

                    agent_input = {"messages": agent_messages}
                    interaction["agent_input"] = agent_input
                    st.session_state.agent_inputs.append(agent_input)

                    with spinner.container():
                        with st.spinner("Thinking... 🤔"):
                            response = agent.invoke(agent_input)
                            assistant_response = response["messages"][-1].content

                # Store terminal output
                terminal_output = stdout.getvalue()
                if terminal_output.strip():
                    st.session_state.terminal_output.append(
                        {"timestamp": timestamp, "output": terminal_output},
                    )

                spinner.empty()
                response_container.markdown(assistant_response)

                # Update interaction with assistant's response
                interaction["assistant_message"] = {
                    "role": "assistant",
                    "content": assistant_response,
                }

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response},
            )
            st.session_state.agent_responses.append(response)

        # Add the complete interaction to the interactions list
        st.session_state.interactions.append(interaction)

# Debug panel
with debug_col:
    debug_tab, terminal_tab = st.tabs(["🔍 Debug", "💻 Terminal"])

    with debug_tab:
        st.title("🔍 Debug Panel")

        try:
            # Display interactions grouped by timestamp
            st.subheader("Interactions")
            if hasattr(st.session_state, "interactions") and st.session_state.interactions:
                for idx, interaction in enumerate(st.session_state.interactions):
                    try:
                        with st.expander(
                            f"Interaction {idx + 1} - {interaction.get('timestamp', 'Unknown time')}",
                            expanded=False,
                        ):
                            tab1, tab2, tab3 = st.tabs(
                                ["User Message", "Assistant Response", "Agent Input"],
                            )

                            with tab1:
                                try:
                                    st.code(
                                        safe_json_serialize(interaction.get("user_message", {})),
                                        language="json",
                                    )
                                except Exception as e:
                                    st.error(f"Error displaying user message: {str(e)}")

                            with tab2:
                                try:
                                    st.code(
                                        safe_json_serialize(interaction.get("assistant_message", {})),
                                        language="json",
                                    )
                                except Exception as e:
                                    st.error(f"Error displaying assistant message: {str(e)}")

                            with tab3:
                                try:
                                    st.code(
                                        safe_json_serialize(interaction.get("agent_input", {})),
                                        language="json",
                                    )
                                except Exception as e:
                                    st.error(f"Error displaying agent input: {str(e)}")
                    except Exception as e:
                        st.error(f"Error displaying interaction {idx + 1}: {str(e)}")
            else:
                st.info("No interactions yet")
        except Exception as e:
            st.error(f"Error in debug panel: {str(e)}")
            st.info("Debug panel encountered an error. The application will continue to work normally.")

    with terminal_tab:
        st.title("💻 Terminal Output")
        if (
            hasattr(st.session_state, "terminal_output")
            and st.session_state.terminal_output
        ):
            for output in st.session_state.terminal_output:
                with st.expander(f"Output at {output['timestamp']}", expanded=False):
                    st.code(output["output"], language="bash")
        else:
            st.info("No terminal output yet")
