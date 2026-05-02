import os
import re
import sqlite3

from dotenv import load_dotenv

try:
    import mysql.connector
except ImportError:
    mysql = None


load_dotenv()

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").strip().lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "chatlogs.db")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_NAME = os.getenv("MYSQL_DATABASE", "ADMISSION_CB")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")


def _safe_identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValueError("MySQL database names can contain only letters, numbers, and underscores.")
    return value


def _sqlite_db_path():
    return os.path.abspath(SQLITE_PATH)


def _sqlite_connect():
    return sqlite3.connect(_sqlite_db_path())


def _mysql_connect(database=None):
    if mysql is None:
        raise RuntimeError(
            "MySQL backend selected, but mysql-connector-python is not installed."
        )

    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }

    if database:
        config["database"] = database

    return mysql.connector.connect(**config)


def _init_mysql_db():
    database = _safe_identifier(DB_NAME)

    conn = _mysql_connect()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
    conn.commit()
    cursor.close()
    conn.close()

    conn = _mysql_connect(database)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ChatLogs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_query TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def _init_sqlite_db():
    conn = _sqlite_connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ChatLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def init_db():
    if DB_BACKEND == "mysql":
        _init_mysql_db()
        return

    if DB_BACKEND != "sqlite":
        raise ValueError("DB_BACKEND must be either 'sqlite' or 'mysql'.")

    _init_sqlite_db()


def save_chat(query, response):
    init_db()

    if DB_BACKEND == "mysql":
        conn = _mysql_connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ChatLogs (user_query, bot_response) VALUES (%s, %s)",
            (query, response),
        )
    else:
        conn = _sqlite_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ChatLogs (user_query, bot_response) VALUES (?, ?)",
            (query, response),
        )

    conn.commit()
    cursor.close()
    conn.close()
