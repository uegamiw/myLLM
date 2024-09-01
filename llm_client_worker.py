from PySide6.QtCore import QThread, Signal
import openai
import anthropic

class Worker(QThread):
    result = Signal(str)

    def __init__(self, prompt, model, logger):
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.logger = logger

    def run(self):
        pass

class OpenAIWorker(Worker):
    def __init__(self, prompt, model, openai_client, logger):
        super().__init__(prompt, model, logger)
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
                model=self.model,
            )
            self.result.emit(response.choices[0].message.content)
        except openai.RateLimitError as e:
            self.result.emit("Error: You have exceeded your quota. Please check your OpenAI plan and billing details.")
            self.logger.error(f"Rate Limit Error: {e}")
        except openai.APIError as e:
            self.result.emit(f"API Error: {e.message}")
            self.logger.error(f"API Error: {e}")
        except Exception as e:
            self.result.emit(f"Unexpected Error: {e}")
            self.logger.error(f"Unexpected Error: {e}")

class AnthropicWorker(Worker):
    def __init__(self, prompt, model, anthropic_client, logger):
        super().__init__(prompt, model, logger)
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
                model=self.model
            )
            self.result.emit(response.content[0].text)
        except anthropic.APIConnectionError as e:
            self.result.emit(f"The server could not be reached: {e.__cause__}")
            self.logger.error(f"API Connection Error: {e}")
        except anthropic.RateLimitError as e:
            self.result.emit("A 429 status code was received; we should back off a bit.")
            self.logger.error(f"Rate Limit Error: {e}")
        except anthropic.APIStatusError as e:
            self.result.emit(f"Another non-200-range status code was received. {e.status_code}, {e.response}")
            self.logger.error(f"API Status Error: {e}")
        except Exception as e:
            self.result.emit(f"Unexpected Error: {e}")
            self.logger.error(f"Unexpected Error: {e}")