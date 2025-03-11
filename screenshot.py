import pyautogui
import time
import os
from core.my_logger import logger


def take_screenshot_monitor(auto_mode=False, interval=60, region=None):
    """
    Создает скриншот второго монитора (или всего экрана, если регион не указан) и сохраняет его на рабочий стол.
    Args:
        auto_mode (bool): Включить автоматический режим (по умолчанию False).
        interval (int): Интервал между скриншотами в секундах (по умолчанию 60).
        region (tuple): Кортеж (x_start, y_start, width, height) для указания региона скриншота (по умолчанию None).
                        Если None, делается скриншот всего экрана.
    Returns:
        str: Путь к сохраненному файлу (для одиночного режима) или None (для автоматического).
    """
    screen_width, screen_height = pyautogui.size()
    logger.info(f"Общий размер экрана: {screen_width}x{screen_height}")

    if region is not None:
        logger.info(f"Регион для скриншота: {region}")
        _save_screenshot(region)
    
    if auto_mode:
        logger.info(f"Автоматический режим включен. Скриншоты будут делаться каждые {interval} секунд. Нажмите Ctrl+C для остановки.")
        try:
            while True:
                _save_screenshot(region)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("\nАвтоматический режим остановлен.")
        return None
    else:
        return _save_screenshot(region)


def _save_screenshot(region):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{'second_monitor' if region else 'full'}_{timestamp}.png"
    save_path = os.path.join(os.path.expanduser("~/scrin_video"), filename)

    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()
    
    screenshot.save(save_path)
    logger.info(f"Скриншот {'второго монитора' if region else 'всего экрана'} сохранен как {save_path}")
    return save_path
