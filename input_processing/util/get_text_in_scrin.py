import os
import re

import pytesseract
from PIL import Image


def extract_text_from_image(image_path, languages="rus+eng"):
    if not os.path.exists(image_path):
        print(f"Ошибка: файл '{image_path}' не найден. Убедитесь, что путь правильный.")
        exit(1)
    try:
        image = Image.open(image_path)
        raw_text = pytesseract.image_to_string(image, lang=languages)
        # normalized_text = normalize_text(raw_text)
        return raw_text
    except Exception as e:
        raise Exception(f"Ошибка при распознавании текста: {str(e)}")


def normalize_text(raw_text):
    """
    Нормализует и группирует распознанный текст для читаемости.

    Args:
        raw_text (str): Сырой текст, полученный от Tesseract.

    Returns:
        str: Отформатированный текст, разделенный на группы.
    """
    # Разделяем текст на строки
    lines = raw_text.splitlines()

    # Инициализируем группы
    grouped_text = {
        "menu": [],  # Элементы интерфейса
        "code": [],  # Код
        "files": [],  # Имена файлов
        "other": [],  # Остальное
    }

    # Регулярные выражения для классификации
    menu_items = r"Файл|Правка|Выделение|Вид|Переход|Выполнить|Терминал|Окно|Справка"
    code_patterns = r"def |import |from |if |elif |else|print\(|=|\b\d+\b"
    file_patterns = r"\.(py|txt|jpg|zip|md|yml|ru)$"

    # Группируем строки
    for line in lines:
        line = line.strip()
        if not line:
            continue

        cleaned_line = re.sub(r"[®@©]\s*", "", line).strip()

        if re.search(menu_items, cleaned_line):
            grouped_text["menu"].append(cleaned_line)
        elif re.search(code_patterns, cleaned_line):
            grouped_text["code"].append(cleaned_line)
        elif re.search(file_patterns, cleaned_line):
            grouped_text["files"].append(cleaned_line)
        else:
            grouped_text["other"].append(cleaned_line)

    formatted_result = ""
    for group, items in grouped_text.items():
        if items:
            formatted_result += f"\n=== {group.upper()} ===\n"
            formatted_result += "\n".join(items) + "\n"

    return formatted_result if formatted_result else "Текст не распознан"
