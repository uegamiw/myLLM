from dataclasses import dataclass, field
import json
from pathlib import Path
from logging import Logger

default_config = {
   "openai_models": {
        "GPT-5.6 Luna": "gpt-5.6-luna",
        "GPT-5.6 Terra": "gpt-5.6-terra",
        "GPT-5.6 Sol": "gpt-5.6-sol"
    },
    "anthropic_models": {
        "Haiku 4.5": "claude-haiku-4-5",
        "Sonnet 5": "claude-sonnet-5",
        "Opus 5": "claude-opus-5",
        "Fable 5": "claude-fable-5"
    },
    "perplexity_models": {
        "Sonar": "sonar",
        "Sonar Pro": "sonar-pro",
        "Sonar Reasoning Pro": "sonar-reasoning-pro",
        "Sonar Deep Research": "sonar-deep-research"
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