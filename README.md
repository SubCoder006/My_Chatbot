# 🤖 NexaBot

A full-stack AI chatbot built with Streamlit, Groq (via LangChain), and Supabase — featuring persistent per-user conversation history, PDF-based conversational RAG, and a ChatGPT-style UI.

Built as a hands-on learning project: from a single-file terminal script to a deployed, multi-user, database-backed AI application.

---

## ✨ Features

- **AI Chat** powered by Groq's free-tier LLMs (via LangChain), with reasoning-tag safety handling
- **Conversational RAG** — attach a PDF and ask questions about it, with query rewriting so follow-up questions ("is that good?") resolve correctly using chat history
- **ChatGPT-style unified input** — one chat box handles both plain messages and PDF attachments (10MB limit)
- **Persistent, per-user chat history** — stored in Supabase (PostgreSQL), retained for 3 days, with a daily message limit
- **User authentication** — email/password login via Supabase Auth; each user only sees their own conversations
- **Sidebar with auto-generated chat titles** — new conversations are automatically titled from the first message, like ChatGPT
- **Dark, gradient-themed UI** — custom CSS chat bubbles (right-aligned user messages, left-aligned bot replies), real avatar images, wide responsive layout
- **Connection pooling** for efficient database access under concurrent use

---

## 🏗️ Architecture

This project deliberately avoids a separate backend framework — **Streamlit serves as both frontend and backend**, calling out to Groq (AI), Supabase (database + auth), and a local FAISS vector store (RAG) directly from the same Python process.

```
User Browser
     │
     ▼
Streamlit App (streamlit_app.py)
     │
     ├── app/core/auth.py              → Supabase Auth (login/signup)
     ├── app/core/conversations.py     → conversation list (per-user)
     ├── app/core/persistent_memory.py → message history + daily limit
     ├── app/core/db.py                → PostgreSQL connection pool (Supabase)
     ├── app/services/chat_service.py  → orchestrates memory + LLM calls
     ├── app/llm/groq_client.py        → LangChain + Groq (ChatGroq)
     └── app/rag/                      → PDF loading, embeddings, retrieval, RAG chain
```

### Design principle
Each layer has exactly one job, and layers only talk to each other through clean function calls — never reaching into each other's internals. This meant that major upgrades (raw Groq SDK → LangChain, SQLite → Supabase Postgres, single-user → multi-user auth) only required rewriting the relevant layer, not the whole app.

---

## 📁 Project Structure

```
Chatbot/
├── app/
│   ├── config.py                  # all settings, loaded from environment variables
│   ├── llm/
│   │   └── groq_client.py         # ChatGroq wrapper, reasoning cleanup, title generation
│   ├── core/
│   │   ├── db.py                  # Postgres connection pool
│   │   ├── auth.py                # Supabase Auth wrapper (sign up/in/out)
│   │   ├── conversations.py       # conversation CRUD, scoped per user
│   │   └── persistent_memory.py   # message storage, retention, daily limit
│   ├── services/
│   │   └── chat_service.py        # send() / send_with_pdf() orchestration
│   └── rag/
│       ├── document_loader.py     # PDF loading + chunking
│       ├── vector_store.py        # embeddings + FAISS similarity search
│       └── rag_chain.py           # query rewriting + retrieval-augmented generation
├── assets/                        # avatar images (robot, human, header logo)
├── .streamlit/
│   └── config.toml                # dark theme settings
├── streamlit_app.py               # main app: auth gate, sidebar, chat UI
├── requirements.txt
├── .env                           # local secrets (not committed)
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI / App server | Streamlit |
| LLM provider | Groq (free tier) |
| LLM orchestration | LangChain (`langchain-groq`, `langchain-core`) |
| Database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth |
| Vector store | FAISS (local, in-memory per session) |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (free, local) |
| PDF parsing | `pypdf` via `langchain-community` |

---

## ⚙️ Setup

### 1. Clone and install
```bash
git clone <your-repo-url>
cd Chatbot
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Get your API keys

- **Groq**: free key at [console.groq.com/keys](https://console.groq.com/keys)
- **Supabase**: create a free project at [supabase.com](https://supabase.com)
  - `DATABASE_URL` → Project → Connect → **Transaction pooler** connection string
  - `SUPABASE_URL` + `SUPABASE_ANON_KEY` → Project Settings → API

### 3. Create `.env` in the project root
```
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

### 4. Run locally
```bash
streamlit run streamlit_app.py
```

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push to GitHub (ensure `.env` is in `.gitignore`)
2. Deploy at [share.streamlit.io](https://share.streamlit.io)
3. Add the same four environment variables under **App Settings → Secrets**, in TOML format:
```toml
GROQ_API_KEY = "..."
DATABASE_URL = "..."
SUPABASE_URL = "..."
SUPABASE_ANON_KEY = "..."
```
4. Under Supabase → Authentication → URL Configuration, add your deployed app's URL as an allowed redirect

---

## 🐛 Notable bugs solved during development

- **Groq model deprecation** — `llama-3.3-70b-versatile` was retired mid-project; migrated to `openai/gpt-oss-120b` / `qwen/qwen3.6-27b`
- **Reasoning tag leakage** — reasoning models leaked `<think>...</think>` blocks into replies; fixed with `reasoning_effort` settings + a regex fallback
- **SQLite → Postgres migration** — required swapping `?` placeholders for `%s`, and manual cursor handling (`psycopg2` doesn't auto-chain like `sqlite3`)
- **Direct vs. pooled DB connections** — Streamlit Cloud couldn't resolve Supabase's direct connection hostname; fixed by switching to the Transaction Pooler connection string
- **Auth/DB URL confusion** — `SUPABASE_URL` (Auth API endpoint) and `DATABASE_URL` (Postgres connection) are distinct credentials from different Supabase dashboard sections

---

## 🚧 Known limitations / next steps

- RAG uses standard vector similarity search — no re-ranking or source citations yet
- No hybrid (keyword + semantic) search
- FAISS vector stores are per-session and in-memory, not persisted across restarts
- Free-tier constraints (Groq rate limits, Supabase connection caps, Streamlit Cloud RAM) limit concurrent usage — suitable for personal/demo use, not high-traffic production

---

## 📄 License

Personal learning project — free to use as reference.