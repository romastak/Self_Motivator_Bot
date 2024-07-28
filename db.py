import sqlite3

# Функция для начального создания таблиц в БД если они отсутствуют
def create_db():
# Создание базы данных
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        name CHAR NOT NULL
    )''')

    # Создание таблицы шаблонов с ID и ключами генерации
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_template (
        user_template_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        template_name CHAR NOT NULL,
        key_for_generating INTEGER,
        FOREIGN KEY (user_id) REFERENCES user (user_id)
    )''')

    # Создание таблицы для хранения структуры шаблона пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS template_structure (
        template_structure_id INTEGER PRIMARY KEY,
        user_template_id INTEGER,
        FOREIGN KEY (user_template_id) REFERENCES user_template (user_template_id)
    )''')

    # Создание таблицы для хранения критериев шаблона
    cursor.execute('''CREATE TABLE IF NOT EXISTS template_critery (
        template_critery_id INTEGER PRIMARY KEY,
        template_structure_id INTEGER,
        critery_name CHAR,
        critery_score FLOAT,
        critery_comment INTEGER,
        FOREIGN KEY (template_structure_id) REFERENCES template_structure (template_structure_id)
    )''')

    # Создание таблицы для хранения множителей шаблона
    cursor.execute('''CREATE TABLE IF NOT EXISTS template_mnojitel (
        template_mnojitel_id INTEGER PRIMARY KEY,
        template_structure_id INTEGER,
        mnojitel_name CHAR,
        mnojitel_score FLOAT,
        mnojitel_comment INT,
        FOREIGN KEY (template_structure_id) REFERENCES template_structure (template_structure_id)
    )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
    print("Database initialized successfully.")