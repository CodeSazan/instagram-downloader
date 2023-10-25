import mysql.connector
from config import *

def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None

def create_table(cursor, table_name, columns):
    if not table_exists(cursor, table_name):
        create_table_query = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns)}
        )
        """
        cursor.execute(create_table_query)

try:
    db = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database= database
    )

    cursor = db.cursor()

    user_columns = [
        "id INT AUTO_INCREMENT PRIMARY KEY",
        "user_id TEXT",
        "ban TEXT NOT NULL",
        "step TEXT NOT NULL"
    ]

    settings_columns = [
        "id VARCHAR(2) PRIMARY KEY",
        "bot TEXT NOT NULL"
    ]

    create_table(cursor, "users", user_columns)
    create_table(cursor, "settings", settings_columns)
    cursor.execute("INSERT INTO settings (id, bot) VALUES (%s, %s)", (1, 'on'))

    db.commit()

except mysql.connector.Error as error:
    print("خطا در اتصال به پایگاه داده:", error)

