from dotenv import load_dotenv
import os
import tiktoken
import argparse
from datetime import datetime
import logging
import re



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Расширения файлов для обработки
TEXT_EXTENSIONS = [
    ".txt",
    ".py",
    ".md",
    ".csv",
    ".js",
    ".html",
    ".css",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".conf",
]

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".vscode",
    ".idea",
    "node_modules",
    ".env",
    "venv",
    "env",
    ".pytest_cache",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
}

IGNORE_FILES = {".DS_Store", ".gitignore", "package-lock.json", "yarn.lock", ".env"}

DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR")

MAX_TOKENS = 10000
ENCODING_NAME = "cl100k_base"

try:
    ENCODING = tiktoken.get_encoding(ENCODING_NAME)
except Exception as e:
    logger.error(
        f"Не удалось получить кодировку tiktoken {ENCODING_NAME}, ошибка: {str(e)}\n"
        "Проверьте, что у вас установлено tiktoken.\n"
        "Установка: pip install tiktoken"
    )
    ENCODING = None


def count_tokens(text: str) -> int:
    """Подсчитывает количество токенов в тексте"""
    if ENCODING is None:
        return len(text.split())
    return len(ENCODING.encode(text))


def clean_content_for_ai_with_comments(content: str, filepath: str) -> str:
    """Очищает содержимое файла от лишних символов для работы с ИИ, сохраняя комментарии"""

    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    content = re.sub(r"[ \t]+", " ", content)

    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def should_ignore_item(item_name: str, is_dir: bool) -> bool:
    """Проверяет, нужно ли игнорировать файл или папку"""
    if item_name.startswith(".") and item_name not in {".env", ".gitignore"}:
        return True

    if is_dir and item_name in IGNORE_DIRS:
        return True

    if not is_dir and item_name in IGNORE_FILES:
        return True

    return False


def process_directory_with_comments(
    directory: str, base_dir: str, target_files: set = None
) -> list:
    """Рекурсивно обрабатывает директорию и возвращает список строк с содержимым файлов (с комментариями)"""
    result_lines = []

    try:
        items = os.listdir(directory)
        items.sort()

        for item in items:
            item_path = os.path.join(directory, item)

            is_dir = os.path.isdir(item_path)
            if should_ignore_item(item, is_dir):
                continue

            try:
                relative_path = os.path.relpath(item_path, base_dir).replace(os.sep, "/")
            except ValueError as e:
                logger.warning(f"Не удалось получить относительный путь для {item_path}: {e}")
                continue

            if os.path.isfile(item_path):
                should_process = False

                if target_files is not None:
                    if relative_path in target_files or item in target_files:
                        should_process = True
                else:
                    if any(item.lower().endswith(ext) for ext in TEXT_EXTENSIONS):
                        should_process = True

                if should_process:
                    try:
                        file_size = os.path.getsize(item_path)
                        if file_size > 1024 * 1024:  # Пропускаем файлы больше 1MB
                            logger.warning(
                                f"Пропускаем большой файл: {relative_path} ({file_size} bytes)"
                            )
                            continue

                        with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        cleaned_content = clean_content_for_ai_with_comments(content, item_path)

                        if cleaned_content.strip():
                            result_lines.append(f"\n=== Файл: {relative_path} ===")
                            result_lines.append(cleaned_content)
                            result_lines.append("=== Конец файла ===\n")
                            logger.info(f"Обработан файл: {relative_path}")

                    except Exception as e:
                        logger.error(f"Ошибка при обработке файла {item_path}: {e}")

            elif os.path.isdir(item_path):
                should_recurse = True
                if target_files is not None:
                    dir_prefix = relative_path + "/"
                    should_recurse = any(target.startswith(dir_prefix) for target in target_files)

                if should_recurse:
                    result_lines.extend(
                        process_directory_with_comments(item_path, base_dir, target_files)
                    )

    except PermissionError:
        logger.warning(f"Нет доступа к директории: {directory}")
    except Exception as e:
        logger.error(f"Ошибка при обработке директории {directory}: {e}")

    return result_lines


def combine_files_from_folder(folder_path: str, target_files: list = None) -> str:
    """
    Главная функция для объединения файлов из папки.
    Возвращает объединенный контент в виде строки вместо создания файлов.
    Сохраняет все комментарии в коде.

    Args:
        folder_path (str): Путь к папке для обработки
        target_files (list): Список конкретных файлов для обработки (опционально)

    Returns:
        str: Объединенный контент всех файлов или пустая строка в случае ошибки
    """

    if not os.path.exists(folder_path):
        logger.error(f"Папка не существует: {folder_path}")
        return ""

    if not os.path.isdir(folder_path):
        logger.error(f"Указанный путь не является папкой: {folder_path}")
        return ""

    # Преобразуем список файлов в множество для быстрого поиска
    target_files_set = set(target_files) if target_files else None

    try:
        logger.info(f"Начинаем обработку папки: {folder_path}")
        all_lines = process_directory_with_comments(folder_path, folder_path, target_files_set)

        if not all_lines:
            logger.warning("Не найдено файлов для обработки")
            return ""

        # Объединяем все строки в один текст
        combined_content = "\n".join(all_lines)

        # Логируем статистику
        total_tokens = count_tokens(combined_content)
        logger.info(
            f"Найдено файлов: {len([line for line in all_lines if line.startswith('=== Файл:')])} "
        )
        logger.info(f"Общее количество токенов: {total_tokens}")
        logger.info(f"Общее количество символов: {len(combined_content)}")

        logger.info("Обработка завершена успешно!")
        return combined_content

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return ""


# Дополнительная функция для совместимости со старым кодом
def split_and_save(lines: list, output_base_path: str):
    """Разбивает содержимое на файлы по лимиту токенов (сохранена для совместимости)"""
    current_part = 1
    current_content = []
    current_tokens = 0

    for line in lines:
        line_tokens = count_tokens(line)

        # Если добавление этой строки превысит лимит и у нас уже есть содержимое
        if current_tokens + line_tokens > MAX_TOKENS and current_content:
            output_path = f"{output_base_path}_part{current_part}.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(current_content) + "\n")

            logger.info(
                f"Сохранена часть {current_part}: {output_path} (токенов: {current_tokens})"
            )
            current_part += 1
            current_content = []
            current_tokens = 0

        current_content.append(line)
        current_tokens += line_tokens

    if current_content:
        if current_part > 1:
            output_path = f"{output_base_path}_part{current_part}.txt"
        else:
            output_path = f"{output_base_path}.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(current_content) + "\n")

        logger.info(f"Сохранена финальная часть: {output_path} (токенов: {current_tokens})")
