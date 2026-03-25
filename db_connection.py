import psycopg2
from psycopg2 import OperationalError


DB_CONFIG = {
    "host": "localhost",
    "database": "technical_support",
    "user": "postgres",
    "password": "12345",
    "port": "5432",
}


def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def init_database():
    conn = get_connection()
    if conn:
        print("✅ Успешное подключение к базе данных PostgreSQL")
        conn.close()
        return True

    print("❌ Не удалось подключиться к базе данных")
    return False