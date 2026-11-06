
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).parent / "lab.db"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                details TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)

        users = [
            (1, "alice", generate_password_hash("alice123"), "user"),
            (2, "bob", generate_password_hash("bob123"), "user"),
            (3, "admin", generate_password_hash("admin123"), "admin")
        ]

        for user in users:
            conn.execute("""
                INSERT OR IGNORE INTO users
                (id, username, password, role)
                VALUES (?, ?, ?, ?)
            """, user)

        invoices = [
            (101, 1, "Alice Laptop Invoice", 1250, "Alice training invoice"),
            (102, 2, "Bob Mobile Invoice", 799, "Bob training invoice"),
            (103, 3, "Admin Server Invoice", 4200, "Admin training invoice")
        ]

        for invoice in invoices:
            conn.execute("""
                INSERT OR IGNORE INTO invoices
                (id, owner_id, title, amount, details)
                VALUES (?, ?, ?, ?, ?)
            """, invoice)

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
