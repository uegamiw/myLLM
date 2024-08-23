import os
import sys
from logging import getLogger, Formatter, DEBUG, INFO, WARNING, ERROR, StreamHandler
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QProgressBar, QRadioButton, QButtonGroup, QHBoxLayout, QLineEdit
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QShortcut, QKeySequence
from openai import OpenAI
import openai
from anthropic import Anthropic
import anthropic
import json

# Initialize the logger
os.makedirs("log", exist_ok=True)
logger = getLogger(__name__)
logger.setLevel(INFO)
sh = StreamHandler()
fh = RotatingFileHandler(
    "log/llm_app.log", maxBytes=1000000, backupCount=5, encoding="utf-8"
    )
sh.setLevel(INFO)
fh.setLevel(INFO)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)  # Add this line to set the formatter
logger.addHandler(sh)
logger.addHandler(fh)

logger.info("App started")

deliminator = " ----- "

# Initialize the OpenAI and Anthropic clients
try:
    api_openai = os.environ.get("OPENAI_API_KEY")
    logger.info(f"OpenAI API Key, loaded")
    client_o = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

except KeyError as e:
    logger.error(f"API Key Error (OpenAI): {e}")
    api_openai = None

try:
    api_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    logger.info(f"Anthropic API Key, loaded")
    client_a = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

except KeyError as e:
    logger.error(f"API Key Error (Anthropic): {e}")
    api_anthropic = None

if api_openai is None and api_anthropic is None:
    logger.critical("API Key Error: Both OpenAI and Anthropic API keys are missing.")
    sys.exit()


# load json
json_path = 'config.json'

with open(json_path, 'r') as f:
    try:
        config = json.load(f)
        logger.info(f"config.json loaded")
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        config = {}
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e}")
        config = {}


openai_models = config.get("openai_models", {})
anthropic_models = config.get("anthropic_models", {})

class Worker(QThread):
    result = Signal(str)

    def __init__(self, prompt, model, system):
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.system = system

        if self.system == "":
            self.system = "user"

    def run(self):

        if self.model in openai_models.keys():
            self.model = openai_models[self.model]
            try:
                response = client_o.chat.completions.create(
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
                logger.error(f"Rate Limit Error: {e}")
            except openai.APIError as e:
                self.result.emit(f"API Error: {e.message}")
                logger.error(f"API Error: {e}")
            except Exception as e:
                self.result.emit(f"Unexpected Error: {e}")
                logger.error(f"Unexpected Error: {e}")

        elif self.model in anthropic_models.keys():
            self.model = anthropic_models[self.model]
            try:
                response = client_a.messages.create(
                    max_tokens=2048,
                    system=self.system,
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
                logger.error(f"API Connection Error: {e}")
            except anthropic.RateLimitError as e:
                self.result.emit("A 429 status code was received; we should back off a bit.")
                logger.error(f"Rate Limit Error: {e}")
            except anthropic.APIStatusError as e:
                self.result.emit(f"Another non-200-range status code was received. {e.status_code}, {e.response}")
                logger.error(f"API Status Error: {e}")
            except Exception as e:
                self.result.emit(f"Unexpected Error: {e}")
                logger.error(f"Unexpected Error: {e}")


class GPTApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("myLLM")
        self.setGeometry(100, 100, 800, 950)

        main_layout = QVBoxLayout()

        preset_layout = QHBoxLayout()

        self.prompts = config.get("prompts", {})

        if self.prompts:
            for prompt_name, prompt_text in self.prompts.items():
                logger.info(f"Prompt loaded: {prompt_name}")
                prompt_text = f"{prompt_text} \n {deliminator} \n"

                button = QPushButton(prompt_name, self)
                button.clicked.connect(lambda checked, p=prompt_text: self.insert_prompt(p))
                preset_layout.addWidget(button)

        else:
            logger.error("No prompts found in the config.json file")

        main_layout.addLayout(preset_layout)

        # text box
        self.text_box = QLineEdit(self, placeholderText="Claude only. Enter system here. (default: user)")
        main_layout.addWidget(self.text_box)
        
        # Input area
        self.text_area = QTextEdit(self, placeholderText="Enter your prompt here")
        main_layout.addWidget(self.text_area)

        # radio buttons for model selection
        self.model_group = QButtonGroup(self)
        model_layout = QHBoxLayout()
        
        if api_openai is not None:
            for openai_model in openai_models.keys():
                logger.info(f"OpenAI model loaded: {openai_model}")
                openai_button = QRadioButton(openai_model, self)
                model_layout.addWidget(openai_button)
                self.model_group.addButton(openai_button)

        if api_anthropic is not None:
            for anthropic_model in anthropic_models.keys():
                logger.info(f"Anthropic model loaded: {anthropic_model}")
                anthropic_button = QRadioButton(anthropic_model, self)
                model_layout.addWidget(anthropic_button)
                self.model_group.addButton(anthropic_button)

        main_layout.addLayout(model_layout)

        # preset the default model
        self.model_group.buttons()[0].setChecked(True)

        # button layout
        button_layout = QHBoxLayout()

        # Send button
        self.send_button = QPushButton("Send (Cmd+Enter)", self)
        self.send_button.clicked.connect(self.on_send)
        button_layout.addWidget(self.send_button)

        # Append button
        self.append_button = QPushButton("Append", self)
        self.append_button.clicked.connect(self.on_append)
        button_layout.addWidget(self.append_button)
        main_layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)

        # Output Area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        main_layout.addWidget(self.output_area)
        self.setLayout(main_layout)

        self.text_area.setFocus()

        # if api_openai is None, show the message to the output area
        if api_openai is None:
            self.output_area.setPlainText("OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable.")
        if api_anthropic is None:
            self.output_area.setPlainText("Anthropic API Key is missing. Please set the ANTHROPIC_API_KEY environment variable.")

        # Shortcut keybind
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.on_send)
        
        mac_shortcut = QShortcut(QKeySequence("Meta+Return"), self)
        mac_shortcut.activated.connect(self.on_send)

    def on_send(self):
        prompt = self.text_area.toPlainText()
        model_button = self.model_group.checkedButton()
        model = model_button.text() if model_button else "gpt-3.5-turbo"
        system = self.text_box.text()
        if prompt:
            logger.info(f"model: {model}, system: {system}, prompt: {prompt}")
            self.progress_bar.setRange(0, 0)  # indeterminate progress bar
            self.worker = Worker(prompt, model, system)
            self.worker.result.connect(self.update_output)
            self.worker.start()

    def update_output(self, response):
        self.progress_bar.setRange(0, 1)  # stop progress bar
        self.output_area.setPlainText(response)
        logger.info(f"response: {response}")

    def on_append(self):
        original_prompt = self.text_area.toPlainText()
        response_txt = self.output_area.toPlainText()
        logger.debug(f"original_prompt: {original_prompt}, response_txt: {response_txt}")

        if original_prompt and response_txt:
            new_prompt = f"{original_prompt}\n{deliminator}\n(Your answer): {response_txt} \n{deliminator}\n"
            self.text_area.setPlainText(new_prompt)
        
        # place the cursor at the end of the text
        cursor = self.text_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End) 
        self.text_area.setTextCursor(cursor)

    def insert_prompt(self, prompt_text):
        self.text_area.setPlainText(prompt_text)
        logger.debug(f"Prompt inserted: {prompt_text}")
        # auto focus on the last line
        cursor = self.text_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_area.setTextCursor(cursor)


def main():
    app = QApplication(sys.argv)
    chatgpt_app = GPTApp()
    chatgpt_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
