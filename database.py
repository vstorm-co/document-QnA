import sqlite3


def init_db():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn


def save_conversation(conn, name):
    c = conn.cursor()
    c.execute("INSERT INTO conversations (name) VALUES (?)", (name,))
    conn.commit()
    return c.lastrowid


def get_conversations(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM conversations ORDER BY created_at DESC")
    return c.fetchall()
