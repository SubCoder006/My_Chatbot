import psycopg2
from psycopg2 import pool
from app.config import DATABASE_URL

_connection_pool = None


def get_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=DATABASE_URL,
        )
    return _connection_pool


def get_connection():
    return get_pool().getconn()


def release_connection(conn):
    get_pool().putconn(conn)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_usage (
            date TEXT PRIMARY KEY,
            message_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    cur.close()
    release_connection(conn)