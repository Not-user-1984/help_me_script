import argparse
from input_processing.screenshot import take_screenshot_monitor
from input_processing.util.get_text_in_scrin import extract_text_from_image
from input_processing.voice_recording import record_and_recognize
from modelAI.chat_sber import GigaChatBot
from modelAI.proxi_api_chat_bot import ProxyAPIChatBot
from core.my_logger import logger
import os


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

    parser.add_argument(
        "--model",
        choices=["giga", "proxy"],
        default="proxy",
        help="Выбор модели чата: 'giga' для GigaChatBot, 'proxy' для ProxyAPIChatBot (по умолчанию: proxy)",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.model == "giga":
        bot = GigaChatBot()
        logger.info("Выбрана модель: GigaChatBot")
    else:
        bot = ProxyAPIChatBot()
        logger.info("Выбрана модель: ProxyAPIChatBot")

    if args.voice:
        logger.info("Запуск голосового ввода...")
        raw_text = record_and_recognize(time_record=30)
        if raw_text:
            logger.info(f"Распознанный текст: {raw_text}")
        else:
            logger.error("Не удалось распознать текст из голоса")
            return

    elif args.screenshot:
        logger.info("Создание скриншота...")
        save_path = take_screenshot_monitor(auto_mode=False, interval=10)
        raw_text = extract_text_from_image(save_path)
        # logger.info(f"Распознанный текст: {raw_text}")
        os.remove(save_path)

    if raw_text:
        bot.process_message(raw_text)

    else:
        logger.error("Не удалось получить текст для обработки")


if __name__ == "__main__":
    main()
