from dataclasses import dataclass, field
import json
from pathlib import Path
from logging import Logger

default_config = {
   "openai_models": {
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o",
        "GPT5-nano": "gpt-5-nano-2025-08-07",
        "GPT5-mini": "gpt-5-mini-2025-08-07",
        "GPT5": "gpt-5-2025-08-07"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3.5 Haiku": "claude-3-5-haiku-latest",
        "Sonnet 3.7": "claude-3-7-sonnet-latest",
        "Sonnet 4": "claude-sonnet-4-20250514",
        "Opus 4": "claude-opus-4-20250514",
        "Opus 4.1": "claude-opus-4-1-20250805"
    },
    "prompts": {
        "Default": "This is a default prompt.",
        "J2E": "Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
    }
}

@dataclass
class Config:
    prompts: dict = field(default_factory=dict)
    openai_models: dict = field(default_factory=dict)
    anthropic_models: dict = field(default_factory=dict)
    perplexity_models: dict = field(default_factory=dict)


class ConfigManager:
    def __init__(self, json_path: Path, logger: Logger) -> None:
        self.json_path = json_path
        self.logger = logger
        self.config = Config()
        self.load_config_json()

    def load_config_json(self) -> Config | None:
        try:
            with open(self.json_path, "r") as f:
                config_dict = json.load(f)
                self.logger.info(f"config.json loaded")
            
            if self.config is not None:
                self.config.prompts = config_dict.get("prompts", {})
                self.config.openai_models = config_dict.get("openai_models", {})
                self.config.anthropic_models = config_dict.get("anthropic_models", {})
                self.config.perplexity_models = config_dict.get("perplexity_models", {})


        except FileNotFoundError as e:
            self.logger.error(f"FileNotFoundError: {e}")

            if self.config is not None:
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

        if self.config is not None:
            if not self.config.prompts:
                self.logger.error("No prompts found in config.json")
                self.config.prompts = default_config["prompts"]

            if not self.config.openai_models and not self.config.anthropic_models:
                self.logger.error("No models found in config.json")
                self.config.openai_models = default_config["openai_models"]
                self.config.anthropic_models = default_config["anthropic_models"]

        return self.config