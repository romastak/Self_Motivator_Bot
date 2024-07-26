import sqlite3

def create_db():
# Создание базы данных
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY
    )''')

    # Создание таблицы шаблонов
    cursor.execute('''CREATE TABLE IF NOT EXISTS templates (
        user_id INTEGER,
        question TEXT,
        response_type TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )''')

    conn.commit()
    conn.close()

