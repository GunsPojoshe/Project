# check_structure.py
import sqlite3

db_path = "instance/sales_funnel.db"

# Функция для проверки структуры таблицы
def print_table_structure(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    if columns:
        print(f"\nСтруктура таблицы '{table_name}':")
        for col in columns:
            print(f"{col[1]} ({col[2]})")
    else:
        print(f"Таблица '{table_name}' не найдена.")
    conn.close()

# Проверяем структуру таблицы sales_funnel
print_table_structure(db_path, "sales_funnel")
