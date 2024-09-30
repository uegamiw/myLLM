from dataclasses import dataclass
import openai
import anthropic
from datetime import datetime
import requests
from PySide6.QtCore import QRunnable, QObject, Signal
from models.chat_parser import ChatParser

@dataclass
class LLMResults:
    prompt: str
    response: str
    model: str
    datetime: str
    id: int = None
    temperature: int = None # 1-10

class WorkerSignals(QObject):
    result = Signal(dict)

class Worker(QRunnable):
    def __init__(self, prompt, model_key,model_val,temp, logger):
        super().__init__()
        self.prompt = prompt
        self.model_key = model_key
        self.model_val = model_val
        self.logger = logger
        self.temp = temp
        self.signals = WorkerSignals()
        self.chart_parser = ChatParser(logger)

    def run(self):
        pass

class OpenAIWorker(Worker):
    def __init__(self, prompt,model_key, model_val, openai_client,temp, logger):
        super().__init__(prompt, model_key, model_val,temp, logger)
        self.openai_client = openai_client

    def run(self):
        chat = self.chart_parser.parse(self.prompt)
        try:
            response = self.openai_client.chat.completions.create(
                messages=chat,
                model=self.model_val,
                temperature=self.temp/5,
            )
            response = response.choices[0].message.content
        except openai.RateLimitError as e:
            response = "Error: You have exceeded your quota. Please check your OpenAI plan and billing details."
            self.logger.error(f"Rate Limit Error: {e}")
        except openai.APIError as e:
            self.logger.error(f"API Error: {e}")
            response = f"API Error: {e.message}"
        except Exception as e:
            self.logger.error(f"Unexpected Error: {e}")
            response = f"Unexpected Error: {e}"

        finally:
            self.signals.result.emit(
                {
                'prompt': self.chart_parser.to_str(chat),
                'response': response,
                'model': self.model_key,
                'datetime': datetime.now().isoformat(),
                'temperature': self.temp
                }
            )


class AnthropicWorker(Worker):
    def __init__(self, prompt, model_key, model_val, anthropic_client,temp, logger):
        super().__init__(prompt, model_key, model_val,temp, logger)
        self.anthropic_client = anthropic_client

    def run(self):
        chat = self.chart_parser.parse(self.prompt, allow_system=False)
        try:
            response = self.anthropic_client.messages.create(
                max_tokens=2048,
                system='user',
                messages=chat,
                model=self.model_val,
                temperature=self.temp/10
            )
            response = response.content[0].text
        except anthropic.APIConnectionError as e:
            self.logger.error(f"API Connection Error: {e}")
            response = f"API Connection Error: {e}"
        except anthropic.RateLimitError as e:
            self.logger.error(f"Rate Limit Error: {e}")
            response = f"Rate Limit Error: {e}"
        except anthropic.APIStatusError as e:
            self.logger.error(f"API Status Error: {e}")
            response = f"API Status Error: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected Error: {e}")
            response = f"Unexpected Error: {e}"

        finally:
            self.signals.result.emit(
                {
                'prompt': self.chart_parser.to_str(chat),
                'response': response,
                'model': self.model_key,
                'datetime': datetime.now().isoformat(),
                'temperature': self.temp
                }
            )


class PerplexityWorker(Worker):

    def __init__(self, prompt, model_key, model_val, perplexity_client, temp, logger):
        super().__init__(prompt, model_key, model_val, temp, logger)
        self.perplexity_client = perplexity_client

    def run(self):
        url = "https://api.perplexity.ai/chat/completions"
        chat = self.chart_parser.parse(self.prompt)
        payload = {
            "model": self.model_val,
            "messages": chat,
            "max_tokens": 2048,
            "temperature": self.temp/5,
            "top_p": 0.9,
            "return_citations": True,
            "search_domain_filter": ["-perplexity.ai"],
            "return_images": False,
            "return_related_questions": True,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        headers = {
            "Authorization": f"Bearer {self.perplexity_client.api_key}",
            "Content-Type": "application/json"
        }

        try:
            print(payload)
            response = requests.request("POST", url, json=payload, headers=headers)
            print(response.text)

            # analyze the response (json format)
            response = response.json()
            response = response['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Error: {e}")
            response = f"Request Error: {e}"

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e}")
            response = f"HTTP Error: {e}"

        # json error
        except ValueError as e:
            self.logger.error(f"JSON Error: {e}")
            response = f"JSON Error: {e}"

        except KeyError as e:
            self.logger.error(f"Key Error: {e}")
            response = f"Key Error: {e}"

        except Exception as e:
            self.logger.error(f"Unexpected Error: {e}")
            response = f"Unexpected Error: {e}"

        finally:
            self.signals.result.emit(
                {
                'prompt': self.chart_parser.to_str(chat),
                'response': response,
                'model': self.model_key,
                'datetime': datetime.now().isoformat(),
                'temperature': self.temp
                }
            )

