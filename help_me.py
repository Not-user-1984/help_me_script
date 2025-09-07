import argparse
import os
import time
import threading
from core.my_logger import logger
from core.settings import settings
from input_processing.screenshot import take_screenshot_monitor
from input_processing.util.get_text_in_scrin import extract_text_from_image
from input_processing.voice_recording import record_and_recognize
from input_processing.file_local.folder_combiner import combine_files_from_folder, DEFAULT_OUTPUT_DIR
from modelAI.chat_sber import GigaChatBot
from modelAI.proxi_api_chat_bot import ProxyAPIChatBot


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Консольный скрипт для общения с чат-ботом через голос или скриншот"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--voice",
        action="store_true",
        help="Использовать голосовой ввод (запись 30 секунд)",
    )
    input_group.add_argument(
        "--screenshot",
        action="store_true",
        help="Использовать скриншот для извлечения текста",
    )
    input_group.add_argument(
        "--auto-screenshot",
        type=float,
        metavar="MINUTES",
        help="Автоматические скриншоты каждые N минут (например, --auto-screenshot 1 или --auto-screenshot 0.5)",
    )
    input_group.add_argument(
        "--f",
        action="store_true",
        help="Обработать файлы из папки с использованием дефолтной модели ИИ",
    )

    parser.add_argument(
        "--model",
        choices=["giga", "proxy"],
        default="proxy",
        help="Выбор модели чата: 'giga' для GigaChatBot, 'proxy' для ProxyAPIChatBot (по умолчанию: proxy)",
    )
    parser.add_argument(
        "--folder",
        type=str,
        help="Путь к папке для обработки файлов (используется с --f)",
    )
    return parser.parse_args()


def auto_screenshot_worker(bot, interval_minutes):
    """Функция для автоматического создания скриншотов в отдельном потоке"""
    logger.info(f"Запуск автоматических скриншотов каждые {interval_minutes} минут")

    while True:
        try:
            save_path = take_screenshot_monitor(auto_mode=False, interval=0)
            logger.info(f"Создан автоматический скриншот: {save_path}")

            raw_text = extract_text_from_image(save_path)

            if os.path.exists(save_path):
                os.remove(save_path)

            if raw_text and raw_text.strip():
                logger.info("Обработка текста из автоматического скриншота...")
                bot.process_message(raw_text)
            else:
                logger.warning(
                    "Не удалось извлечь текст из автоматического скриншота или текст пустой"
                )

        except Exception as e:
            logger.error(f"Ошибка при создании автоматического скриншота: {e}")

        time.sleep(interval_minutes * 60)


def process_folder_files(bot, folder_path=None):
    """Функция для обработки файлов из папки"""
    if not folder_path:
        # Используем дефолтный путь или текущую директорию
        folder_path = DEFAULT_OUTPUT_DIR

    if not os.path.exists(folder_path):
        logger.error(f"Папка не существует: {folder_path}")
        return

    if not os.path.isdir(folder_path):
        logger.error(f"Указанный путь не является папкой: {folder_path}")
        return

    logger.info(f"Начинаю обработку файлов из папки: {folder_path}")

    try:
        combined_content = combine_files_from_folder(folder_path)
        logger.info(combined_content)

        if combined_content and combined_content.strip():
            logger.info("Найден контент для обработки, отправляю в чат-бот...")
            bot.process_message(combined_content)
        else:
            logger.warning("Не удалось извлечь контент из файлов или контент пустой")

    except Exception as e:
        logger.error(f"Ошибка при обработке файлов из папки: {e}")


def main():
    args = parse_arguments()

    # Для команды --f всегда используем дефолтную модель proxy
    if args.f:
        model_choice = "proxy"
        model_choice = args.model

    if model_choice == "giga":
        bot = GigaChatBot()
        logger.info("Выбрана модель: GigaChatBot")
    else:
        if args.f:
            name_prompt = "file_processing"
        elif args.voice:
            name_prompt = "voice"
        else:
            name_prompt = "default"

        bot = ProxyAPIChatBot(
            name_prompt=name_prompt,
            api_url=settings.url_proxi_api_openai,
            model=settings.gpt4,
        )
        logger.info(f"Выбрана модель: ProxyAPIChatBot с промтом: {name_prompt}")

    if args.voice:
        logger.info("Запуск голосового ввода...")
        raw_text = record_and_recognize(time_record=7)
        if raw_text:
            logger.info(f"Распознанный текст: {raw_text}")
            bot.process_message(raw_text)
        else:
            logger.error("Не удалось распознать текст из голоса")
            return

    elif args.screenshot:
        logger.info("Создание скриншота...")
        save_path = take_screenshot_monitor(auto_mode=False, interval=10)
        raw_text = extract_text_from_image(save_path)
        os.remove(save_path)

        if raw_text:
            bot.process_message(raw_text)
        else:
            logger.error("Не удалось получить текст для обработки")

    elif args.auto_screenshot:
        if args.auto_screenshot <= 0:
            logger.error("Интервал для автоматических скриншотов должен быть положительным числом")
            return

        logger.info(f"Запуск режима автоматических скриншотов каждые {args.auto_screenshot} минут")
        logger.info("Для остановки нажмите Ctrl+C")

        screenshot_thread = threading.Thread(
            target=auto_screenshot_worker, args=(bot, args.auto_screenshot), daemon=True
        )
        screenshot_thread.start()

        try:
            screenshot_thread.join()
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки. Завершение работы...")
            return

    elif args.f:
        logger.info("Запуск режима обработки файлов...")
        process_folder_files(bot, args.folder)


if __name__ == "__main__":
    main()
