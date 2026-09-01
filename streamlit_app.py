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
# st.sidebar                  → a persistent panel pinned to the left,
#                                 used here for the conversation list
# st.rerun()                  → forces Streamlit to re-run the whole
#                                 script immediately (used after actions
#                                 like switching/deleting a conversation,
#                                 so the UI reflects the change right away)
# ─────────────────────────────────────────────────────────────────────

import base64
import tempfile
import streamlit as st
from app.core.persistent_memory import PersistentMemory, DailyLimitExceeded
from app.core.conversations import create_conversation, list_conversations, update_conversation_title, delete_conversation
from app.services.chat_service import ChatService
from app.llm.groq_client import generate_title
from app.rag.document_loader import load_and_chunk_pdf
from app.rag.vector_store import build_vector_store
from app.core.auth import sign_out,sign_in,sign_up


# ── Auth gate: block everything below until logged in ──
if "user" not in st.session_state:
    st.markdown("""
    <style>
    .login-header {
        text-align: center;
        padding: 40px 0 10px 0;
    }
    .login-header h1 {
        font-size: 42px;
        background: linear-gradient(135deg, #7C3AED, #4F46E5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .login-header p {
        color: gray;
        font-size: 16px;
    }
    </style>
    <div class="login-header">
        <h1>🤖 NexaBot</h1>
        <p>Your personal AI assistant — log in to continue</p>
    </div>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Log In", use_container_width=True):
                try:
                    result = sign_in(email, password)
                    st.session_state.user = result.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

        with tab2:
            new_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
            new_password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up", use_container_width=True):
                try:
                    sign_up(new_email, new_password)
                    st.success("Account created! Check your email to confirm, then log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

    st.stop()

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

st.set_page_config(page_title="NexaBot", page_icon="assets/robot.png", layout="wide")

# ── Custom CSS for chat bubbles ─────────────────────────────
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    margin: 0 auto;
    padding-top: 2rem;
}
.chat-row {
    display:flex;
    align-items:flex-start;
    margin:16px 0;
    gap:10px;
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
    object-fit: cover;
}
.bubble {
    max-width: 75%;
    padding:14px 18px;
    border-radius:18px;
    line-height:1.6;
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


def load_conversation(conversation_id):
    memory = PersistentMemory(conversation_id)
    st.session_state.current_conversation_id = conversation_id
    st.session_state.chat_service = ChatService(memory)
    st.session_state.chat_history = [(role, text) for role, text in memory.get_full_history()]
    st.session_state.vector_store = None
    st.session_state.attached_file_name = None


def start_new_chat():
    new_id = create_conversation(st.session_state.user.id, "New chat")
    load_conversation(new_id)


# ── Sidebar: conversation list ─────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 NexaBot")
    if st.button("🚪 Log Out", use_container_width=True):
        sign_out()
        del st.session_state.user
        st.rerun()
    st.markdown("---")
    if st.button("➕ New Chat", use_container_width=True):
        ...

    st.markdown("---")
    st.caption("Chats")

    for conv_id, title in list_conversations(st.session_state.user.id):
        is_active = st.session_state.get("current_conversation_id") == conv_id
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(title, key=f"conv_{conv_id}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                load_conversation(conv_id)
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv_id}"):
                delete_conversation(conv_id)
                if is_active:
                    st.session_state.current_conversation_id = None
                st.rerun()

# ── Load first/active conversation ─────────────────────────────
if "current_conversation_id" not in st.session_state:
    existing = list_conversations(st.session_state.user.id)
    load_conversation(existing[0][0]) if existing else start_new_chat()

# ── Header (unchanged from your original) ─────────────────────────────
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

# redraw every past message
for role, text in st.session_state.chat_history:
    render_message(role, text)

if st.session_state.get("attached_file_name"):
    st.info(f"📎 Currently chatting with: {st.session_state.attached_file_name}")

prompt = st.chat_input(
    "Message NexaBot, or attach a PDF (max 10MB)...",
    accept_file=True,
    file_type=["pdf"],
)

if prompt:
    if prompt.files:
        uploaded_file = prompt.files[0]
        if len(uploaded_file.getvalue()) > MAX_FILE_SIZE_BYTES:
            st.error(f"'{uploaded_file.name}' is too large. Max size is {MAX_FILE_SIZE_MB}MB.")
        else:
            with st.spinner("Reading and indexing your PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                chunks = load_and_chunk_pdf(tmp_path)
                st.session_state.vector_store = build_vector_store(chunks)
                st.session_state.attached_file_name = uploaded_file.name
            st.success(f"'{uploaded_file.name}' is ready — ask away!")

    if prompt.text:
        is_first_message = len(st.session_state.chat_history) == 0

        st.session_state.chat_history.append(("user", prompt.text))
        render_message("user", prompt.text)

        try:
            if st.session_state.get("vector_store") is not None:
                reply = st.session_state.chat_service.send_with_pdf(prompt.text, st.session_state.vector_store)
            else:
                reply = st.session_state.chat_service.send(prompt.text)

            st.session_state.chat_history.append(("assistant", reply))
            render_message("assistant", reply)

            if is_first_message:
                title = generate_title(prompt.text)
                update_conversation_title(st.session_state.current_conversation_id, title)
                st.rerun()

        except DailyLimitExceeded as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong: {e}")