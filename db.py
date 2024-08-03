import psycopg2
import configparser


def get_connection_and_cursor_vars():
    # Чтение конфигурационных данных из config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    host = config['db']['host']
    user = config['db']['user']
    password = config['db']['password']
    db_name = config['db']['db_name']
    port = config['db']['port']

    # Получаем connection и cursor for db
    connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
    cursor = connection.cursor()

    return connection, cursor

connection, cursor = get_connection_and_cursor_vars()

def create_db_if_not_exist(connection, cursor):

    # Функция для создания таблицы если она отсутствует
    def check_table_exists_and_create(cursor, table_name, create_table_sql):
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """)
        exists = cursor.fetchone()[0]

        if exists:
            print(f"[INFO] Table '{table_name}' already exists.")
            # Действия, если таблица существует
        else:
            cursor.execute(create_table_sql)
            connection.commit()
            print(f"[INFO] Table '{table_name}' created successfully.")
            # Действия, если таблица не существует

    try:
        # Проверка и создание таблицы пользователей
        check_table_exists_and_create(
            cursor,
            "user",
            '''CREATE TABLE "user" (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT,
                username TEXT
            );'''
        )

        # Проверка и создание таблицы user_template
        check_table_exists_and_create(
            cursor,
            "user_template",
            '''CREATE TABLE user_template (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL, 
                template_name TEXT,
                key_for_generating TEXT,
                FOREIGN KEY (user_id) REFERENCES "user" (id)
            );'''
        )

        # Проверка и создание таблицы template_structure
        check_table_exists_and_create(
            cursor,
            "template_structure",
            '''CREATE TABLE template_structure (
                id SERIAL PRIMARY KEY,
                user_template_id INT NOT NULL,
                FOREIGN KEY (user_template_id) REFERENCES user_template (id)
            );'''
        )

        # Проверка и создание таблицы template_critery
        check_table_exists_and_create(
            cursor,
            "template_critery",
            '''CREATE TABLE template_critery (
                id SERIAL PRIMARY KEY,
                template_structure_id INT NOT NULL,
                critery_name TEXT,
                critery_score TEXT,
                critery_comment TEXT,
                FOREIGN KEY (template_structure_id) REFERENCES template_structure (id)
            );'''
        )

        # Проверка и создание таблицы template_mnojitel
        check_table_exists_and_create(
            cursor,
            "template_mnojitel",
            '''CREATE TABLE template_mnojitel (
                id SERIAL PRIMARY KEY,
                template_structure_id INT NOT NULL,
                mnojitel_name TEXT,
                mnojitel_score TEXT,
                mnojitel_comment TEXT,
                FOREIGN KEY (template_structure_id) REFERENCES template_structure (id)
            );'''
        )

    except Exception as _ex:
        print("[INFO] Ошибка взаимодействия с БД", _ex)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] PostgreSQL connection closed")

# Используем этот модуль как точка входа для создания таблиц
if __name__ == '__main__':
    create_db_if_not_exist(connection, cursor)