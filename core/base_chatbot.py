from abc import ABC, abstractmethod

import pyperclip
import yaml
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.syntax import Syntax

from rich.markdown import Markdown
from core.my_logger import logger


class BaseChatBot(ABC):
    """Абстрактный класс для чат-ботов с разными AI-моделями."""

    def __init__(self, config_path="config.json", name_prompt="default"):
        self.console = Console()
        self.config_path = config_path
        self.name_prompt = name_prompt
        self.messages = [SystemMessage(content=self.load_prompt(self.name_prompt))]

    def load_prompt(self, name_prompt):
        """
        Загружает промт из JSON-файла.

        Returns:
            str: Загруженный промт или значение по умолчанию.
        """
        if name_prompt is not None:
            self.name_prompt = name_prompt
        try:
            with open("prompt/gigachat.yaml", "r", encoding="utf-8") as file:
                prompts = yaml.safe_load(file)
            return prompts[self.name_prompt]
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.error(f"Ошибка загрузки промта: {str(e)}")
            return "Введите задачу для решения"

    @abstractmethod
    def generate_response(self, user_input):
        """Метод должен быть реализован в подклассах для взаимодействия с конкретной AI-моделью."""
        pass

    def process_message(self, user_input):
        """
        Обрабатывает сообщение пользователя и возвращает ответ бота.

        Args:
            user_input (str): Ввод пользователя.

        Returns:
            str: Ответ бота.
        """
        try:
            self.messages.append(HumanMessage(content=user_input))
            res = self.generate_response(user_input)
            self.messages.append(res)
            # self.console.print(Markdown(res.content))
            # logger.info(f" Ответ бота: {res.content}")

            if "```python" in res.content:
                code = res.content.split("```python")[1].split("```")[0].strip()
                syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                self.console.print(syntax)
                # pyperclip.copy(code)
                self.console.print("[bold green]Код скопирован в буфер обмена![/bold green]")
            else:
                self.console.print(Markdown(res.content))

            return res.content
        except Exception as e:
            logger.error(f"Ошибка в работе бота: {str(e)}")
            return f"Произошла ошибка: {str(e)}"
