import os
import zipfile

def write_project_overview(output_file):
    """
    Добавляет справку о проекте в начало файла.
    :param output_file: Файл для записи результата.
    """
    overview_text = """Привет, мы работаем через VS Code на Windows.

Проект использует следующие технологии:
- Python (Flask, SQLAlchemy, Flask-WTF, Flask-Login, Flask-Migrate, Werkzeug)
- HTML/CSS (анимации, адаптивный дизайн)
- JavaScript (Canvas, динамическая анимация частиц)
- PostgreSQL (в качестве базы данных)
- VS Code (как основное средство разработки)

Информация о базе данных:
- Тип базы данных: PostgreSQL
- URL базы данных: postgresql://postgres:password@localhost/unit_metrica
- Миграции управляются с помощью Flask-Migrate.

Используемые библиотеки Python:
- Flask: Для создания веб-приложения
- SQLAlchemy: Для работы с базой данных
- Flask-WTF: Для работы с формами.
- Flask-Login: Для управления сессиями пользователей
- Flask-Migrate: Для управления миграциями базы данных
- Werkzeug: Для работы с паролями и безопасности
"""
    with open(output_file, 'a', encoding='utf-8') as out:
        out.write(overview_text + "\n\n" + "=" * 50 + "\n\n")

def list_core_app_files(base_path, extensions, output_file, max_files=100, exclude_dirs=None):
    """
    Рекурсивно обходит директорию core_app, записывает пути файлов и их содержимое в файл.
    Исключает определённые директории.
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv', '__pycache__', '.git']

    file_count = 0
    with open(output_file, 'a', encoding='utf-8') as out:
        out.write("Содержимое файлов в директории core_app:\n\n")
        for root, dirs, files in os.walk(base_path):
            # Исключение директорий
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file_count >= max_files:
                    out.write(f"Обработка остановлена: достигнуто максимальное количество файлов ({max_files}).\n")
                    return
                if any(file.endswith(ext) for ext in extensions):
                    file_count += 1
                    file_path = os.path.join(root, file)
                    out.write(f"Файл: {file_path}\n{'-' * 50}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"Ошибка при чтении файла: {e}\n")
                    out.write("\n" + "=" * 50 + "\n\n")

def print_specific_files(files, output_file):
    """
    Записывает содержимое определённых файлов в файл.
    :param files: Список путей к файлам.
    :param output_file: Файл для записи результата.
    """
    with open(output_file, 'a', encoding='utf-8') as out:
        out.write("Содержимое отдельных файлов:\n\n")
        for file_path in files:
            out.write(f"Файл: {file_path}\n{'-' * 50}\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"Ошибка при чтении файла: {e}\n")
            out.write("\n" + "=" * 50 + "\n\n")

def write_final_message(output_file):
    """
    Добавляет финальное сообщение в файл.
    :param output_file: Файл для записи результата.
    """
    final_message = "Запомни всё и жди моих указаний."
    with open(output_file, 'a', encoding='utf-8') as out:
        out.write(final_message + "\n")

def split_output_into_files_and_zip(base_filename, content, max_lines=3000, zip_filename="output_files.zip"):
    """
    Разделяет текстовый контент на несколько файлов, если он превышает лимит строк, и архивирует их.
    :param base_filename: Базовое имя файла.
    :param content: Текстовый контент для разделения.
    :param max_lines: Максимальное количество строк в одном файле.
    :param zip_filename: Имя ZIP-архива для созданных файлов.
    """
    lines = content.splitlines()  # Разделение текста на строки
    file_count = 1  # Счетчик для имен файлов

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i in range(0, len(lines), max_lines):
            # Извлекаем блок строк
            part = "\n".join(lines[i:i + max_lines])
            filename = f"{base_filename}_{file_count}.txt"
            
            # Создаём временный файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(part)

            # Добавляем файл в архив
            zipf.write(filename, arcname=os.path.basename(filename))
            print(f"Добавлено в архив: {filename} ({len(part.splitlines())} строк).")
            
            # Удаляем временный файл после добавления в архив
            os.remove(filename)
            
            file_count += 1
            
            # Ограничение на количество создаваемых файлов
            if file_count > 100:  # Лимит для предотвращения ошибок
                print("Превышено максимальное количество файлов! Прерывание.")
                break

    print(f"Архив создан: {zip_filename}")

if __name__ == "__main__":
    # Путь к папке core_app и файлы для анализа
    core_app_directory = "C:/Games/PROJECT"
    specific_files = [
        "C:/Games/PROJECT/run.py",
        "C:/Games/PROJECT/config.py"
    ]
    file_extensions = [".py", ".html", ".css", ".js"]
    base_output_file = "C:/Games/PROJECT/output"

    # Очистка файла перед записью
    with open(base_output_file + "_1.txt", 'w', encoding='utf-8') as f:
        f.write("")

    # Добавление справки о проекте
    write_project_overview(base_output_file + "_1.txt")
    
    # Вывод содержимого файлов из core_app
    list_core_app_files(core_app_directory, file_extensions, base_output_file + "_1.txt")
    
    # Вывод содержимого указанных файлов
    print_specific_files(specific_files, base_output_file + "_1.txt")
    
    # Добавление финального сообщения
    write_final_message(base_output_file + "_1.txt")

    # Чтение содержимого для разделения
    with open(base_output_file + "_1.txt", 'r', encoding='utf-8') as f:
        content = f.read()

# Разделяем контент на части по 10000 строк и архивируем их
split_output_into_files_and_zip(base_output_file, content, max_lines=3000, zip_filename="output_files.zip")
