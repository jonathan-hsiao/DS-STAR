from abc import ABC, abstractmethod
from typing import Optional
import os

from google import genai
import openai

class BaseProvider(ABC):
    """ Base class for LLM providers. """

    def __init__(
        self, 
        model: str, 
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """ Generate a response from the LLM. """
        pass


class GeminiProvider(BaseProvider):
    """ Provider for Gemini models. """

    def __init__(
        self, 
        model: str = "gemini-2.5-pro", 
        api_key: Optional[str] = None,
    ):
        super().__init__(model, api_key)
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=self.api_key)

    def generate_response(
        self, 
        prompt: str,
    ) -> str:
        """ Generate a response from the LLM. """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


class OpenAIProvider(BaseProvider):
    """ Provider for OpenAI models. """

    def __init__(
        self, 
        model: str = "gpt-5.2", 
        api_key: Optional[str] = None,
    ):
        super().__init__(model, api_key)
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(
        self, 
        prompt: str,
    ) -> str:
        """ Generate a response from the LLM. """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content