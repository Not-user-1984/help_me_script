from langchain_gigachat.chat_models import GigaChat
from core.settings import settings
from langchain_core.messages import AIMessage
from core.my_logger import logger
from core.base_chatbot import BaseChatBot


class GigaChatBot(BaseChatBot):
    """Класс чат-бота, использующего GigaChat."""

    def __init__(self, config_path="prompt/gigachat.yaml", name_prompt="default", model='GigaChat-2'):
        super().__init__(config_path, name_prompt)
        self.giga = GigaChat(
            credentials=settings.api_sber_gigachat,
            model=model,
            verify_ssl_certs=False)

    def generate_response(self, user_input):
        """Генерирует ответ с помощью GigaChat."""
        try:
            self.messages
            response = self.giga.invoke(self.messages)
            return AIMessage(content=response.content)
        except Exception as e:
            logger.error(f"Ошибка в GigaChat: {str(e)}")
            return AIMessage(content=f"Ошибка: {str(e)}")
