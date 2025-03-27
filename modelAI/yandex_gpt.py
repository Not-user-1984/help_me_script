import requests
from langchain_core.messages import AIMessage

from core.base_chatbot import (
    BaseChatBot,
)
from core.my_logger import logger
from core.settings import settings


class YandexChatBot(BaseChatBot):
    """Чат-бот для работы с YandexGPT через API."""

    def __init__(
        self, config_path="config.json", name_prompt="default", model="yandexgpt"
    ):
        super().__init__(config_path, name_prompt)
        self.folder_id = settings.yandex_id_folder
        self.iam_token = settings.yandex_iam_token
        self.api_url = settings.url_YandexGPT
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}",
        }
        self.model_uri = f"gpt://{self.folder_id}/{model}"

    def generate_response(self, user_input):
        """
        Генерирует ответ с использованием YandexGPT API.

        Args:
            user_input (str): Ввод пользователя.

        Returns:
            AIMessage: Ответ от модели.
        """
        try:
            payload = {
                "modelUri": self.model_uri,
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": "2000",
                },
                "messages": [
                    {"role": "system", "text": self.load_prompt(self.name_prompt)},
                    {"role": "user", "text": user_input},
                ],
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()

            result = response.json()
            generated_text = result["result"]["alternatives"][0]["message"]["text"]
            return AIMessage(content=generated_text)

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к YandexGPT API: {str(e)}")
            return AIMessage(content=f"Ошибка API: {str(e)}")
        except KeyError as e:
            logger.error(f"Ошибка разбора ответа от YandexGPT: {str(e)}")
            return AIMessage(content="Ошибка обработки ответа от сервера")
