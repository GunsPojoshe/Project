#check_db.py#
import sqlite3

# Подключаемся к базе данных
connection = sqlite3.connect("C:/Games/PROJECT/instance/sales_funnel.db")

# Создаём курсор для выполнения запросов
cursor = connection.cursor()

# Проверяем список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Выводим таблицы
if tables:
    print("Таблицы в базе данных:")
    for table in tables:
        print(f"- {table[0]}")
else:
    print("Нет таблиц в базе данных.")

# Закрываем соединение
connection.close()

import sqlite3

db_path = "instance/sales_funnel.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Выполняем запрос для выгрузки всех данных
cursor.execute("SELECT * FROM sales_funnel;")
rows = cursor.fetchall()

# Выводим все строки
for row in rows:
    print(row)

print(f"Всего строк: {len(rows)}")

conn.close()

