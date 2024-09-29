import os
from openai import OpenAI
from anthropic import Anthropic
from logging import Logger
import requests

class Perplexity_client:
    def __init__(self, api_key):
        self.api_key = api_key

class APIClientManager:
    def __init__(self, logger: Logger) -> None:
        self.openai_client = None
        self.anthropic_client = None
        self.perplexity_client = None
        self.logger = logger

        self.get_openai_client()
        self.get_anthropic_client()
        self.get_perplexity_client()

    def get_openai_client(self):
        try:
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            self.logger.info(f"OpenAI client initialized")
        except KeyError as e:
            self.logger.error(f"API Key Error (OpenAI): {e}")
        except Exception as e:
            self.logger.error(f"Error (OpenAI): {e}")

    def get_anthropic_client(self):
        try:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            self.anthropic_client = Anthropic(api_key=api_key)
            if api_key is None:
                self.anthropic_client = None
                self.logger.error(f"Anthropic client not initialized")
            else:
                self.logger.info(f"Anthropic client initialized")
        except KeyError as e:
            self.logger.error(f"API Key Error (Anthropic): {e}")
        except Exception as e:
            self.logger.error(f"Error (Anthropic): {e}")

    def get_perplexity_client(self):
        try:
            api_key = os.environ.get("PERPLEXITY_API_KEY")
            self.perplexity_client = Perplexity_client(api_key)
            self.logger.info(f"Perplexity client initialized")
        except KeyError as e:
            self.logger.error(f"API Key Error (Perplexity): {e}")
        except Exception as e:
            self.logger.error(f"Error (Perplexity): {e}")