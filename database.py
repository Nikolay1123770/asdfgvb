import sqlite3

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_text TEXT NOT NULL,
        used INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        key_id INTEGER,
        amount REAL,
        status TEXT,
        invoice_id TEXT
    )
    """)
    conn.commit()

def add_key(key_text):
    cursor.execute("INSERT INTO keys (key_text) VALUES (?)", (key_text,))
    conn.commit()

def get_unused_key():
    cursor.execute("SELECT id, key_text FROM keys WHERE used=0 LIMIT 1")
    return cursor.fetchone()

def mark_key_used(key_id):
    cursor.execute("UPDATE keys SET used=1 WHERE id=?", (key_id,))
    conn.commit()

def create_order(user_id, key_id, amount, status, invoice_id):
    cursor.execute(
        "INSERT INTO orders (user_id, key_id, amount, status, invoice_id) VALUES (?, ?, ?, ?, ?)",
        (user_id, key_id, amount, status, invoice_id)
    )
    conn.commit()

def update_order_status(invoice_id, status):
    cursor.execute("UPDATE orders SET status=? WHERE invoice_id=?", (status, invoice_id))
    conn.commit()

def get_order_by_invoice(invoice_id):
    cursor.execute("SELECT * FROM orders WHERE invoice_id=?", (invoice_id,))
    return cursor.fetchone()
