# ── Streamlit functions used in this file ──────────────────────────────
# st.title(text)              → shows a large page heading at the top
# st.session_state            → a dict-like store that survives across
#                                 reruns (Streamlit reruns the whole script
#                                 on every user interaction, so normal
#                                 variables would reset each time)
# st.chat_message(role)       → renders a styled chat bubble; role is
#                                 "user" or "assistant", used as a `with`
#                                 block so anything inside it appears
#                                 inside that bubble
# st.chat_input(placeholder)  → a text box pinned to the bottom of the
#                                 page; returns the typed text once Enter
#                                 is pressed, otherwise returns None
# st.write(text)              → generic "display this" function; prints
#                                 text (or other objects) to the page
# st.error(text)              → shows text in a red error box, used for
#                                 exceptions/failures
# ─────────────────────────────────────────────────────────────────────

import base64
import streamlit as st
from app.core.memory import ConversationMemory
from app.services.chat_service import ChatService

st.set_page_config(page_title="My Chatbot", page_icon="assets/robot.png", layout="centered")

# ── Custom CSS for chat bubbles ─────────────────────────────
st.markdown("""
<style>
.chat-row {
    display: flex;
    align-items: flex-end;
    margin: 12px 0;
    gap: 8px;
    max-width: 80%;
}
.chat-row.user {
    flex-direction: row-reverse;
    margin-left: auto;
}
.chat-row.bot {
    margin-right: auto;
}
.avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: contain;
}
.bubble {
    padding: 12px 16px;
    border-radius: 16px;
    line-height: 1.5;
    color: white;
}
.bubble.user {
    background: linear-gradient(135deg, #7C3AED, #4F46E5);
    border-bottom-right-radius: 4px;
}
.bubble.bot {
    background: linear-gradient(135deg, #2D2D3A, #1E1E2E);
    border: 1px solid #3A3A4A;
    border-bottom-left-radius: 4px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


robot_b64 = get_base64_image("assets/robot.png")
human_b64 = get_base64_image("assets/human.png")


def render_message(role, text):
    css_class = "bot" if role == "assistant" else "user"
    avatar_b64 = robot_b64 if role == "assistant" else human_b64
    st.markdown(f"""
    <div class="chat-row {css_class}">
        <div class="avatar"><img src="data:image/png;base64,{avatar_b64}"></div>
        <div class="bubble {css_class}">{text}</div>
    </div>
    """, unsafe_allow_html=True)

header_robot_b64 = get_base64_image("assets/robo.png")

st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{header_robot_b64}" 
             style="width:80px; height:80px; border-radius:50%;">
        <h1>🤖 NexaBot</h1>
        <p style="font-size:18px;color:gray;">
            Powered by Groq AI 🚀
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if "chat_service" not in st.session_state:
    memory = ConversationMemory()
    st.session_state.chat_service = ChatService(memory)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# redraw every past message
for role, text in st.session_state.chat_history:
    render_message(role, text)

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    render_message("user", user_input)

    try:
        reply = st.session_state.chat_service.send(user_input)
        st.session_state.chat_history.append(("assistant", reply))
        render_message("assistant", reply)
    except Exception as e:
        st.error(f"Something went wrong: {e}")