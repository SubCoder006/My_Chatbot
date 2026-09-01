import uuid
from datetime import datetime
from app.core.db import get_connection, init_db, release_connection


def create_conversation(user_id, title="New chat"):
    init_db()
    conversation_id = str(uuid.uuid4())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (id, user_id, title, created_at) VALUES (%s, %s, %s, %s)",
        (conversation_id, user_id, title, datetime.now().isoformat()),
    )
    conn.commit()
    cur.close()
    release_connection(conn)
    return conversation_id


def list_conversations(user_id):
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title FROM conversations WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def update_conversation_title(conversation_id, title):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE conversations SET title = %s WHERE id = %s", (title, conversation_id))
    conn.commit()
    cur.close()
    release_connection(conn)


def delete_conversation(conversation_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
    cur.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
    conn.commit()
    cur.close()
    release_connection(conn)