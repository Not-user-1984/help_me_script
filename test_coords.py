import pyautogui
import time

# Проверяем общий размер экрана
screen_width, screen_height = pyautogui.size()
print(f"Общий размер экрана: {screen_width}x{screen_height}")

# Проверяем координаты курсора
print("Переместите курсор в верхний левый угол второго монитора (LG HDR QHD) и подождите 5 секунд...")
time.sleep(5)
x, y = pyautogui.position()
print(f"Координаты курсора: x={x}, y={y}")