from dataclasses import dataclass
import openai
import anthropic
from datetime import datetime
from PySide6.QtCore import QRunnable, QObject, Signal

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

    def run(self):
        pass

class OpenAIWorker(Worker):
    def __init__(self, prompt,model_key, model_val, openai_client,temp, logger):
        super().__init__(prompt, model_key, model_val,temp, logger)
        self.openai_client = openai_client

    def run(self):
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {
                        "role": 'user',
                        "content": self.prompt,
                    }
                ],
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
                'prompt': self.prompt,
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
        try:
            response = self.anthropic_client.messages.create(
                max_tokens=2048,
                system='user',
                messages=[
                    {
                        "role": 'user',
                        "content": self.prompt,
                    },
                ],
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
                'prompt': self.prompt,
                'response': response,
                'model': self.model_key,
                'datetime': datetime.now().isoformat(),
                'temperature': self.temp
                }
            )