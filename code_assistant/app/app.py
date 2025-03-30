"""Streamlit application for the Code Assistant chat interface."""

import contextlib
import datetime
from io import StringIO
import json

import streamlit as st

from code_assistant.app.agent import agent
from code_assistant.config import get_settings

# Load settings
settings = get_settings()

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

        # Display interactions grouped by timestamp
        st.subheader("Interactions")
        if hasattr(st.session_state, "interactions") and st.session_state.interactions:
            for idx, interaction in enumerate(st.session_state.interactions):
                with st.expander(
                    f"Interaction {idx + 1} - {interaction['timestamp']}",
                    expanded=False,
                ):
                    tab1, tab2, tab3 = st.tabs(
                        ["User Message", "Assistant Response", "Agent Input"],
                    )

                    with tab1:
                        st.code(
                            json.dumps(interaction["user_message"], indent=2),
                            language="json",
                        )

                    with tab2:
                        st.code(
                            json.dumps(interaction["assistant_message"], indent=2),
                            language="json",
                        )

                    with tab3:
                        st.code(
                            json.dumps(interaction["agent_input"], indent=2),
                            language="json",
                        )
        else:
            st.info("No interactions yet")

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
