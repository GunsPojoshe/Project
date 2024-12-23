# load_sales_data.py #

import os
import sqlite3
import pandas as pd
import re
from datetime import datetime

# Путь к файлу Excel и базе данных
folder_path = r"C:/Games/PROJECT/xls/sales/WILDBERRIES/ВоронкаПродаж"
db_path = "C:/Games/PROJECT/instance/sales_funnel.db"

# Подключение к базе данных
conn = sqlite3.connect(db_path)

# Функция для полного удаления таблицы
def drop_table(table_name="sales_funnel"):
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"Таблица '{table_name}' успешно удалена.")
    except Exception as e:
        print(f"Ошибка при удалении таблицы: {e}")

# Функция для преобразования дат из 'd-m-yyyy' в 'yyyy-mm-dd'
def convert_date(date_str):
    day, month, year = date_str.split('-')
    return f"{year}-{month}-{day}"

# Функция для очистки имени столбца для SQL (замена пробела на подчеркивание, удаление нежелательных символов)
def clean_column_name(column_name):
    # Убираем лишние пробелы, символы % и запятые в имени столбца
    column_name = column_name.replace(' ', '_').replace('(', '').replace(')', '').replace('%', '').replace(',', '')
    return column_name

# Функция для обработки дублирующихся столбцов
def handle_duplicate_columns(df):
    seen = {}
    for i, column in enumerate(df.columns):
        if column in seen:
            # Если столбец уже встречался, добавляем суффикс (1), (2) и т.д.
            seen[column] += 1
            df.columns.values[i] = f"{column}_{seen[column]}"
        else:
            seen[column] = 0
    return df

# Функция для создания таблицы динамически
def create_table(df, table_name="sales_funnel"):
    cursor = conn.cursor()
    
    # Генерация столбцов для таблицы из DataFrame с учетом типов данных
    columns = [f"{clean_column_name(col)} TEXT" for col in df.columns]
    
    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {', '.join(columns)})"
    print("Create table query:", create_query)  # Для отладки

    cursor.execute(create_query)
    conn.commit()

# Функция для загрузки всех данных и динамического создания таблицы
def load_data(file_path, table_name="sales_funnel"):
    try:
        # Читаем данные из Excel (лист "Товары")
        df = pd.read_excel(file_path, sheet_name='Товары', skiprows=1)

        # Обрабатываем дублирующиеся столбцы
        df = handle_duplicate_columns(df)

        # Переименовываем столбцы в соответствии с нужной структурой
        df.columns = [clean_column_name(col) for col in df.columns]  # Очистка имен столбцов

        # Извлекаем даты начала и конца периода из имени файла
        filename = os.path.basename(file_path)
        date_pattern = r"(\d{1,2}-\d{1,2}-\d{4})"
        dates = re.findall(date_pattern, filename)

        if len(dates) >= 2:
            start_date = convert_date(dates[1])  # Начало периода (например, 1-10-2024)
            end_date = convert_date(dates[2])  # Конец периода (например, 31-10-2024)
        else:
            start_date = end_date = None  # Если не удалось извлечь даты

        # Добавляем колонки start_date и end_date в DataFrame
        df['start_date'] = start_date
        df['end_date'] = end_date

        # Создаём таблицу динамически
        create_table(df, table_name)

        # Загружаем данные в таблицу sales_funnel
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Данные из файла '{file_path}' успешно загружены.")
    except Exception as e:
        print(f"Ошибка при обработке файла '{file_path}': {e}")
        import traceback
        traceback.print_exc()

# Удаляем существующую таблицу
drop_table()

# Загружаем данные из Excel
files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
for file_path in files:
    load_data(file_path)

# Закрываем подключение
conn.close()
print("Загрузка данных завершена.")
