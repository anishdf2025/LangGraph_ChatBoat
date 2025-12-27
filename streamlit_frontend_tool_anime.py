import streamlit as st
from langgraph_tool_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# =========================== Page Config ===========================
st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================== Custom CSS ===========================
st.markdown("""
<style>
    /* Animated gradient background */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    /* Sidebar neon styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%);
        border-right: 2px solid #00f2ff;
        box-shadow: 5px 0 30px rgba(0, 242, 255, 0.3);
    }
    
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #00f2ff 0%, #ff00ea 100%) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.5) !important;
        transition: all 0.4s ease !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 0 30px rgba(255, 0, 234, 0.8), 0 0 50px rgba(0, 242, 255, 0.5) !important;
    }
    
    /* Sidebar text styling */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] .element-container {
        color: #00f2ff !important;
        text-shadow: 0 0 10px #00f2ff, 0 0 20px #ff00ea;
    }
    
    /* Chat messages with glow */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 242, 255, 0.2);
        animation: messageGlow 2s ease-in-out infinite;
    }
    
    @keyframes messageGlow {
        0%, 100% { box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 242, 255, 0.2); }
        50% { box-shadow: 0 8px 32px rgba(0, 242, 255, 0.4), 0 0 30px rgba(255, 0, 234, 0.3); }
    }
    
    /* User message neon effect */
    div[data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #ff00ea 0%, #00f2ff 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 20px rgba(255, 0, 234, 0.6) !important;
    }
    
    /* Chat input glow */
    .stChatInputContainer {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 2px solid #00f2ff !important;
        border-radius: 30px !important;
        box-shadow: 0 5px 25px rgba(0, 242, 255, 0.4) !important;
    }
    
    /* Headers with neon glow */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.8), 
                     0 0 20px rgba(255, 0, 234, 0.6),
                     0 0 30px rgba(0, 242, 255, 0.4) !important;
        font-weight: 900 !important;
        letter-spacing: 2px;
        animation: neonPulse 2s ease-in-out infinite;
    }
    
    @keyframes neonPulse {
        0%, 100% { text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff, 0 0 30px #ff00ea; }
        50% { text-shadow: 0 0 20px #00f2ff, 0 0 40px #00f2ff, 0 0 60px #ff00ea; }
    }
    
    /* Status box anime style */
    .stStatus {
        background: rgba(26, 26, 46, 0.9) !important;
        border-left: 4px solid #00f2ff !important;
        border-right: 4px solid #ff00ea !important;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.3) !important;
    }
    
    /* Scrollbar neon */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(26, 26, 46, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00f2ff 0%, #ff00ea 100%);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.8);
    }
    
    /* Main content area */
    .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get("messages", [])

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
with st.sidebar:
    st.markdown("# 🤖 AI ASSISTANT")
    st.markdown("---")
    
    if st.button("✨ NEW CHAT", use_container_width=True):
        reset_chat()
        st.rerun()
    
    st.markdown("### 💬 CONVERSATIONS")
    st.markdown("---")
    
    if len(st.session_state["chat_threads"]) == 0:
        st.info("No conversations yet!")
    
    for idx, thread_id in enumerate(st.session_state["chat_threads"][::-1]):
        is_current = thread_id == st.session_state["thread_id"]
        button_label = f"{'🟢' if is_current else '💭'} Chat {len(st.session_state['chat_threads']) - idx}"
        
        if st.button(button_label, key=f"thread_{thread_id}", use_container_width=True):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)
            temp_messages = []
            for msg in messages:
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                temp_messages.append({"role": role, "content": msg.content})
            st.session_state["message_history"] = temp_messages
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(0, 242, 255, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid #00f2ff;'>
    <p style='font-size: 0.9rem; margin: 0; color: white;'>
    ⚡ Powered by <b>LangGraph</b><br>
    🚀 Your AI Assistant
    </p>
    </div>
    """, unsafe_allow_html=True)

# ============================ Main UI ============================
st.markdown("""
<div style='text-align: center; padding: 2rem 0; background: rgba(0, 0, 0, 0.3); border-radius: 20px; margin: 1rem 0;'>
    <h1 style='font-size: 3.5rem; margin: 0; color: #00f2ff; text-shadow: 0 0 20px #00f2ff, 0 0 40px #ff00ea, 0 0 60px #00f2ff;'>
        🤖 AI ASSISTANT
    </h1>
    <p style='color: #ffffff; font-size: 1.3rem; margin: 1rem 0; text-shadow: 0 0 10px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 242, 255, 0.8);'>
        ✨ How can I help you today? ✨
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Welcome message
if len(st.session_state["message_history"]) == 0:
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0; background: rgba(0, 0, 0, 0.2); border-radius: 20px; border: 2px solid rgba(0, 242, 255, 0.3);'>
        <h2 style='font-size: 2.5rem; color: #00f2ff; text-shadow: 0 0 15px #00f2ff, 0 0 30px #ff00ea;'>
            👋 Welcome!
        </h2>
        <p style='color: #ffffff; font-size: 1.3rem; margin: 1rem 0; text-shadow: 0 0 10px rgba(0, 0, 0, 0.8), 0 0 15px rgba(255, 0, 234, 0.6);'>
            🌟 Start your conversation below 🌟
        </p>
    </div>
    """, unsafe_allow_html=True)

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

user_input = st.chat_input("💭 Type your message here...")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant", avatar="🤖"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )