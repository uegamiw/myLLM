from dataclasses import dataclass
import json
from pathlib import Path
from logging import Logger

default_config = {
    "openai_models": {
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3 Sonnet": "claude-3-sonnet-20240229",
        "Claude3.5 Sonnet": "claude-3-5-sonnet-20240620",
    },
    "perplexity_models": {
        "Sonar_3.1_8B": "llama-3.1-sonar-small-128k-online",
        "Sonar_3.1_70B": "llama-3.1-sonar-large-128k-online",
        "Sonar_3.1_405B": "llama-3.1-sonar-huge-128k-online"
    },
    "prompts": {
        "Default": "This is a default prompt.",
        "J2E": "Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
    }
}

@dataclass
class Config:
    prompts: dict = None
    openai_models: dict = None
    anthropic_models: dict = None
    perplexity_models: dict = None


class ConfigManager:
    def __init__(self, json_path: Path, logger: Logger) -> None:
        self.json_path = json_path
        self.logger = logger
        self.config = Config()
        self.load_config_json()

    def load_config_json(self) -> dict:
        try:
            with open(self.json_path, "r") as f:
                config_dict = json.load(f)
                self.logger.info(f"config.json loaded")
            
            self.config.prompts = config_dict.get("prompts", {})
            self.config.openai_models = config_dict.get("openai_models", {})
            self.config.anthropic_models = config_dict.get("anthropic_models", {})
            self.config.perplexity_models = config_dict.get("perplexity_models", {})


        except FileNotFoundError as e:
            self.logger.error(f"FileNotFoundError: {e}")

            self.config.prompts = default_config["prompts"]
            self.config.openai_models = default_config["openai_models"]
            self.config.anthropic_models = default_config["anthropic_models"]
            self.config.perplexity_models = default_config["perplexity_models"]

            # save the default configuration
            with open(self.json_path, "w") as f:
                json.dump(default_config, f, indent=4)
                self.logger.info(f"config.json auto-generated")

        except json.JSONDecodeError as e:
            self.logger.critical(f"JSONDecodeError: {e}")
            self.config = None
        except Exception as e:
            self.logger.critical(f"Unexpected Error: {e}")
            self.config = None

        if not self.config.prompts:
            self.logger.error("No prompts found in config.json")
            self.config.prompts = default_config["prompts"]

        if not self.config.openai_models and not self.config.anthropic_models:
            self.logger.error("No models found in config.json")
            self.config.openai_models = default_config["openai_models"]
            self.config.anthropic_models = default_config["anthropic_models"]

        return self.config