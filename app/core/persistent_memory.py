
from datetime import datetime, timedelta
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config import SYSTEM_PROMPT, MEMORY_RETENTION_DAYS, CONTEXT_WINDOW_MESSAGES, DAILY_MESSAGE_LIMIT
from app.core.db import get_connection, init_db, release_connection


class DailyLimitExceeded(Exception):
    pass


class PersistentMemory:
    def __init__(self, conversation_id):
        init_db()
        self.conversation_id = conversation_id
        self._cleanup_old_messages()

    def _cleanup_old_messages(self):
        cutoff = (datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)).isoformat()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE created_at < %s", (cutoff,))
        conn.commit()
        cur.close()
        release_connection(conn)

    def _today_key(self):
        return datetime.now().strftime("%Y-%m-%d")

    def check_daily_limit(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT message_count FROM daily_usage WHERE date = %s", (self._today_key(),))
        row = cur.fetchone()
        cur.close()
        release_connection(conn)
        count = row[0] if row else 0
        if count >= DAILY_MESSAGE_LIMIT:
            raise DailyLimitExceeded(
                f"Daily limit of {DAILY_MESSAGE_LIMIT} messages reached. Try again tomorrow."
            )

    def _increment_daily_count(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO daily_usage (date, message_count) VALUES (%s, 1)
            ON CONFLICT (date) DO UPDATE SET message_count = daily_usage.message_count + 1
            """,
            (self._today_key(),),
        )
        conn.commit()
        cur.close()
        release_connection(conn)

    def add_user_message(self, content):
        self.check_daily_limit()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (%s, %s, %s, %s)",
            (self.conversation_id, "user", content, datetime.now().isoformat()),
        )
        conn.commit()
        cur.close()
        release_connection(conn)
        self._increment_daily_count()

    def add_assistant_message(self, content):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (%s, %s, %s, %s)",
            (self.conversation_id, "assistant", content, datetime.now().isoformat()),
        )
        conn.commit()
        cur.close()
        release_connection(conn)

    def undo_last_user_message(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM messages WHERE conversation_id = %s AND role = 'user' ORDER BY id DESC LIMIT 1",
            (self.conversation_id,),
        )
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM messages WHERE id = %s", (row[0],))
            conn.commit()
        cur.close()
        release_connection(conn)

    def get_full_history(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY id ASC",
            (self.conversation_id,),
        )
        rows = cur.fetchall()
        cur.close()
        release_connection(conn)
        return rows

    def get_messages(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY id DESC LIMIT %s",
            (self.conversation_id, CONTEXT_WINDOW_MESSAGES),
        )
        rows = cur.fetchall()
        cur.close()
        release_connection(conn)
        rows.reverse()

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for role, content in rows:
            messages.append(HumanMessage(content=content) if role == "user" else AIMessage(content=content))
        return messages