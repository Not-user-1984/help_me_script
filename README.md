# Help Me Script

`help_me.py` — это консольный скрипт на Python, который позволяет взаимодействовать с чат-ботами через голосовой ввод или текст, извлеченный из скриншотов. Поддерживаются две модели чат-ботов: `GigaChatBot` (от Сбера) и `ProxyAPIChatBot` (через ProxyAPI). Скрипт использует флаги командной строки для выбора метода ввода и модели.

---

## Требования

- Python 3.6+
- Установленные зависимости (см. `requirements.txt` ниже)
- Доступ к микрофону (для голосового ввода)
- Подключение к интернету (для работы с API чат-ботов)
- API-ключи для выбранной модели чат-бота (см. раздел [Получение API-ключей](#получение-api-ключей))

---

## Установка

1. Склонируйте репозиторий или сохраните файл `help_me.py` в рабочую директорию.
2. Создайте виртуальное окружение (опционально):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Настройте API-ключи в файле `.env` (см. [Настройка токенов](#настройка-токенов)).

---

## Получение API-ключей

Для работы скрипта необходимо получить API-ключи для выбранной модели чат-бота.

### GigaChatBot
- **Источник**: [Документация GigaChat API](https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-create-project)
- **Инструкция**:
  -  Зарегистрируйтесь в [личном кабинете Studio](https://developers.sber.ru) через Сбер ID.
- **Особенности**:
  - Новым пользователям доступен бесплатный тариф `Freemium` с ограниченным количеством токенов.
  - Базовая модель (например, `GigaChat-Lite`) довольно слабая, но для тестов подходит.
  - Более мощные модели (например, `GigaChat-Pro`) доступны с лимитами на токены.
- **Использование в `help_me.py`**:
  - Укажите модель через параметр `model` в конструкторе:
    ```python
    bot = GigaChatBot(model="GigaChat-Pro")  # Замените на нужную модель
    ```
  - Список доступных моделей указан в документации.

### ProxyAPIChatBot
- **Источник**: [ProxyAPI](https://proxyapi.ru/)
- **Инструкция**:
  - Зарегистрируйтесь на сайте, используя email.

- **Особенности**:
  - Использует прокси для доступа к моделям OpenAI, DeepSeek, Gemini, Claude и др.
  - Платный сервис (от 200 рублей), но старые модели (например, `gpt-3.5-turbo`) бюджетны.
  - По умолчанию используется `gpt-3.5-turbo`.
  - Доступные модели указаны на сайте; можно указать другую модель в настройках:
    ```python
    bot = ProxyAPIChatBot(model="gpt-4o")  # Пример с другой моделью
    ```
- **Преимущества**:
  - Работает без VPN, оплата в рублях.

---

## Настройка токенов

Токены для авторизации хранятся в файле `.env` в корневой директории проекта. Пример структуры файла:

```plaintext
# .env
GIGACHAT_API_KEY=ваш_ключ_для_GigaChat
PROXYAPI_API_KEY=ваш_ключ_для_ProxyAPI
```

Для загрузки токенов в скрипт используйте библиотеку `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env
gigachat_key = os.getenv("GIGACHAT_API_KEY")
proxyapi_key = os.getenv("PROXYAPI_API_KEY")
```

Передавайте ключи в конструкторы чат-ботов:
```python
bot = GigaChatBot(api_key=gigachat_key, model="GigaChat-Pro")
# или
bot = ProxyAPIChatBot(api_key=proxyapi_key, model="gpt-3.5-turbo")
```


---

## Дополнительная настройка

### Аудиоввод
Для работы голосового ввода через `speech_recognition` требуется установка `PyAudio`:

- **Windows**:
  ```bash
  pip install pipwin
  pipwin install PyAudio
  ```
- **Linux**: 
  ```bash
  sudo apt install python3-pyaudio
  ```
- **macOS**: 
  ```bash
  pip install PyAudio
  ```

## Промты

Можно править в файле prompt/gigachat.yaml, указывать модели `GigaChatBot` и `ProxyAPIChatBot`, какой брать через аргумент name_prompt="название из файла" по умолчанию default.

### Извлечение текста из скриншотов (OCR)
Для работы модуля `pytesseract` необходимо установить `Tesseract OCR`:

#### Установка Tesseract OCR
- **Windows**: 
  - Скачайте и установите [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
  - Добавьте путь к `tesseract.exe` (например, `C:\Program Files\Tesseract-OCR`) в переменную PATH.
  - Альтернативно, через Chocolatey:
    ```bash
    choco install tesseract
    ```
- **Linux**: 
  ```bash
  sudo apt install tesseract-ocr
  ```
- **macOS**: 
  ```bash
  brew install tesseract
  ```

#### Поддержка русского языка
Для распознавания текста на русском языке установите языковой пакет:
- **Windows/Linux**: Скачайте `rus.traineddata` с [репозитория Tesseract](https://github.com/tesseract-ocr/tessdata) и поместите в папку `tessdata` (обычно `C:\Program Files\Tesseract-OCR\tessdata` на Windows или `/usr/share/tesseract-ocr/4.00/tessdata` на Linux).
- **macOS**: 
  ```bash
  brew install tesseract-lang
  ```

### Примечание о кроссплатформенности
- Код протестирован только на **macOS**.
- Реализация модулей `/input_processing/screenshot.py` и `/input_processing/voice_recording.py` может потребовать доработки под вашу ОС (Windows/Linux). Например:
  - На Windows учитывайте масштабирование DPI для скриншотов с помощью `pyautogui`.
  - На Linux проверьте доступность микрофона и совместимость с `PyAudio`.

---

### Общий синтаксис
```bash
python help_me.py [ФЛАГ_ВВОДА] [--model МОДЕЛЬ]
```

### Флаги ввода
Вы должны выбрать один из следующих методов ввода (они взаимоисключающие):

- `--voice`: Использовать голосовой ввод (запись аудио длительностью 30 секунд).
- `--screenshot`: Сделать скриншот и извлечь текст из изображения.
- `--f`: работа с файлами, в input_processing/file_local/folder_combiner.py можно указать DEFAULT_OUTPUT_DIR

### Флаг модели
- `--model`: Выбор модели чат-бота:
  - `giga`: Использовать `GigaChatBot`.
  - `proxy`: Использовать `ProxyAPIChatBot` (значение по умолчанию).

### Примеры команд

1. **Голосовой ввод с ProxyAPIChatBot (по умолчанию)**:
   ```bash
   python help_me.py --voice
   ```
   - Запустит запись голоса на 30 секунд, распознает речь на русском языке и отправит текст в `ProxyAPIChatBot`.

2. **Скриншот с GigaChatBot**:
   ```bash
   python help_me.py --screenshot --model giga
   ```
   - Сделает скриншот, извлечет текст и отправит его в `GigaChatBot`.

3. **Голосовой ввод с GigaChatBot**:
   ```bash
   python help_me.py --voice --model giga
   ```
   - Запишет голос и отправит распознанный текст в `GigaChatBot`.

4. **Скриншот с ProxyAPIChatBot**:
   ```bash
   python help_me.py --screenshot
   ```
   - Сделает скриншот, извлечет текст и отправит его в `ProxyAPIChatBot`.

### Ограничения
- Нельзя использовать `--voice` и `--screenshot` одновременно (они взаимоисключающие).
- Для голосового ввода требуется рабочий микрофон.
- Для скриншотов требуется правильная настройка модуля `take_screenshot_monitor`.


---

## Ограничения и совместимость

- **Проверено**: Работоспособность подтверждена только на macOS.
- **Windows/Linux**: Реализация `screenshot.py` и `voice_recording.py` может отличаться:
  - Для скриншотов на Windows используйте `pyautogui` с учетом масштабирования DPI.
  - Для голосового ввода на Windows установите `PyAudio`.
- **OCR**: Для извлечения текста из скриншотов требуется `pytesseract` и установленный `tesseract-ocr`.

---

## Устранение неполадок

- **"Не удалось распознать речь"**: Проверьте микрофон и установку `PyAudio`.
- **"Ошибка Tesseract"**: Убедитесь, что `tesseract-ocr` установлен и доступен в PATH.
- **"API ключ не работает"**: Проверьте правильность токенов в `.env`.
