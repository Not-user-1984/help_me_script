import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Settings:
    """Класс для хранения настроек API и модели."""

    api_sber_gigachat: str = os.getenv("API_SBER_GIGACHAT")
    deepseek_api_key: str = os.getenv("API_KEY_DEEP_SEEK")
    deepseek_base_url: str = "https://api.deepseek.com"
    open_ai_model: str = "deepseek-chat"
    proxi_ai_api: str = os.getenv("API_KEY_PROXI_API")


settings = Settings()
