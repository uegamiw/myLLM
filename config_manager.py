import json
from pathlib import Path
from logging import Logger

default_config = {
    "openai_models": {
        "GPT3.5":"gpt-3.5-turbo",
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3 Sonnet": "claude-3-sonnet-20240229",
        "Claude3.5 Sonnet": "claude-3-5-sonnet-20240620",
    },
    "prompts": {
        "Default": "This is a default prompt.",
        "J2E": "Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
    }
}

class ConfigManager:
    def __init__(self, json_path: Path, logger: Logger) -> None:
        self.json_path = json_path
        self.logger = logger
        self.config = self.load_config()

    def load_config(self) -> dict:
        try:
            with open(self.json_path, "r") as f:
                config = json.load(f)
                self.logger.info(f"config.json loaded")
        except FileNotFoundError as e:
            self.logger.error(f"FileNotFoundError: {e}")
            config = default_config

            # save the default configuration
            with open(self.json_path, "w") as f:
                json.dump(default_config, f, indent=4)
                self.logger.info(f"config.json auto-generated")

        except json.JSONDecodeError as e:
            self.logger.critical(f"JSONDecodeError: {e}")
            config = {}
        except Exception as e:
            self.logger.critical(f"Unexpected Error: {e}")
            config = {}
        return config