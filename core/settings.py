import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


DEEPSEEK_API_KEY = os.getenv("API_KEY_DEEP_SEEK")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"