import streamlit as st
from langchain_agent import create_aub_agent, process_user_query
from langchain_community.callbacks import StreamlitCallbackHandler
from utils import escape_markdown

import os
# Page configuration
st.set_page_config(
    page_title="AUB Student Assistant",
    page_icon="🎓"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = create_aub_agent()

# Available programs
PROGRAMS = [
    "Cybersecurity Online Diploma",
    "AI & Data Science Programs",
    "Project Management",
    "UX/UI Design",
    "Sustainability in Built Environment",
    "Information Technology & Computing",
    "AI Starter Kit"
]

def limit_messages():
    """Keep only the last 6 messages (3 exchanges)"""
    if len(st.session_state.messages) > 6:
        st.session_state.messages = st.session_state.messages[-6:]

# Sidebar
with st.sidebar:
    st.header("AUB Student Assistant")
    st.write("AI agent powered by LangChain that intelligently uses tools to search the knowledge base.")
    
    # Settings
    st.subheader("Settings")
    st.session_state.verbose = True
    
    # Clear chat
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("AUB Student Assistant")
st.write("Ask me anything about AUB programs - I use advanced AI tools to find the best information for you.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Use st.text for assistant responses to prevent $ breaking Markdown
        if message["role"] == "assistant":
            st.markdown(escape_markdown(message["content"]))
        else:
            st.markdown(message["content"])

# Footer placeholder
footer_placeholder = st.empty()

# Only show footer if no user messages yet
if len([m for m in st.session_state.messages if m.get("role") == "user"]) == 0:
    with footer_placeholder.container():
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**LangChain Agent**")
            st.markdown("Advanced AI agent with tool usage")
        with col2:
            st.markdown("**Smart Tool Selection**")
            st.markdown("Automatically chooses the best search method")
        with col3:
            st.markdown("**Memory Management**")
            st.markdown("Maintains context while staying efficient")

# Chat input
if user_input := st.chat_input("Type your question about AUB programs..."):
    # Remove footer immediately
    footer_placeholder.empty()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Process with spinner and agent
    with st.spinner("Agent is thinking and using tools..."):
        try:
            streamlit_callback = None
            result = process_user_query(
                agent=st.session_state.agent,
                user_input=user_input,
                chat_history=st.session_state.messages[:-1],
                verbose=True,
                streamlit_callback=streamlit_callback
            )
            response = result["response"]
            tools_used = result.get("tools_used", [])
            # Always show logs (function call and LLM response)
            if tools_used:
                display_response = f"Function(s) called: {', '.join(tools_used)}\n\n{response}"
            else:
                display_response = response

            with st.chat_message("assistant"):
                st.markdown(escape_markdown(display_response))

            message_data = {
                "role": "assistant", 
                "content": display_response,
                "show_details": False,
                "details": ""
            }
            st.session_state.messages.append(message_data)
            limit_messages()
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            with st.chat_message("assistant"):
                st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            # Limit message history even on error
            limit_messages()
