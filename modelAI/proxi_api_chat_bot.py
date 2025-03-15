import requests
from langchain_core.messages import AIMessage
from core.settings import settings
from core.my_logger import logger
from core.base_chatbot import (
    BaseChatBot,
)


class ProxyAPIChatBot(BaseChatBot):
    """Чат-бот для взаимодействия с моделью через ProxyAPI."""

    def __init__(
        self,
        config_path="prompt/gigachat.yaml",
        name_prompt="default",
        model="gpt-3.5-turbo",
    ):
        super().__init__(config_path, name_prompt)
        self.api_url = "https://api.proxyapi.ru/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.proxi_ai_api}",
        }
        self.model = model

    def generate_response(self, user_input):
        """Генерирует ответ от модели через HTTP-запрос к ProxyAPI."""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.messages[0].content,
                    },
                    {"role": "user", "content": user_input},
                ],
                "temperature": 0.7,
            }
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            bot_response = data["choices"][0]["message"]["content"]

            return AIMessage(content=bot_response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API: {str(e)}")
            return AIMessage(content=f"Ошибка при обращении к API: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Ошибка разбора ответа API: {str(e)}")
            return AIMessage(content=f"Ошибка обработки ответа: {str(e)}")
