import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Класс для хранения настроек API и модели."""

    api_sber_gigachat: str = os.getenv("API_SBER_GIGACHAT")
    proxi_ai_api: str = os.getenv("API_KEY_PROXI_API")
    yandex_iam_token: str = os.getenv("YANDEX_IAM_TOKEN")
    yandex_id_folder: str = os.getenv("YANDEX_ID_FOLDER")

    # urls
    url_proxi_api_openai = os.getenv("URl_PROXI_API_OPENAI")
    url_proxi_api_claude = os.getenv("URl_PROXI_API_ClAUDE")
    url_proxi_api_deeepseek = os.getenv("URl_PROXI_API_DEEPSEEK")
    url_YandexGPT = os.getenv("URL_YANDEX_GPT")

    # models
    gpt4o = "gpt-4o"
    deepseek = "deepseek-chat"
    gpt3 = "gpt-3.5-turbo"
    claude3_7 = "claude-3-7-sonnet-20250219"


settings = Settings()
