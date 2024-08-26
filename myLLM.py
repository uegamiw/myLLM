import os
import sys
from logging import getLogger, Formatter, DEBUG, INFO, WARNING, ERROR, StreamHandler
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QProgressBar, QRadioButton, QButtonGroup, QHBoxLayout, QLineEdit, QMenuBar, QMenu
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QShortcut, QKeySequence, QKeyEvent
from openai import OpenAI
import openai
from anthropic import Anthropic
import anthropic
import json
from pathlib import Path
import messages

json_path = 'config.json'
log_path = Path("log/llm_app.log")

deliminator = " ----- "

class model_clients:
    def __init__(self, logger) -> None:
        self.openai_client = None
        self.anthropic_client = None
        self.logger = logger

    def get_model_clients(self):
        try:
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            self.logger.info(f"OpenAI client initialized")

        except KeyError as e:
            self.logger.error(f"API Key Error (OpenAI): {e}")

        except Exception as e:
            self.logger.error(f"API Key Error (OpenAI): {e}")

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
            self.logger.error(f"API Key Error (Anthropic): {e}")


def load_config(json_path:Path, logger) -> dict:
    # Load the config.json file
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            logger.info(f"config.json loaded")

    except FileNotFoundError as e:
        logger.critical(f"FileNotFoundError: {e}")
        config = {}

    except json.JSONDecodeError as e:
        logger.critical(f"JSONDecodeError: {e}")
        config = {}
    except Exception as e:
        logger.critical(f"Unexpected Error: {e}")
        config = {}
    
    return config

class TextEditWithZoom(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultFontSize = self.font().pointSize()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoomIn()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoomOut()
                return
        super().keyPressEvent(event)

    def zoomIn(self, range=1):
        font = self.font()
        font.setPointSize(font.pointSize() + range)
        self.setFont(font)

    def zoomOut(self, range=1):
        font = self.font()
        newSize = font.pointSize() - range
        if newSize > 0:  # Prevent the font size from becoming negative or too small
            font.setPointSize(newSize)
            self.setFont(font)

class Worker(QThread):
    result = Signal(str)

    def __init__(self, prompt, model, system, openai_models, anthropic_models, openai_client, anthropic_client, logger):
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.system = system
        self.openai_models = openai_models
        self.anthropic_models = anthropic_models
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.logger = logger

        if self.system == "":
            self.system = "user"

    def run(self):

        if self.model in self.openai_models.keys():
            self.model = self.openai_models[self.model]
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

        elif self.model in self.anthropic_models.keys():
            self.model = self.anthropic_models[self.model]
            try:
                response = self.anthropic_client.messages.create(
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


class GPTApp(QWidget):
    def __init__(self, config:dict, clients:model_clients, logger):
        super().__init__()
        self.config = config
        self.openai_clients = clients.openai_client
        self.anthropic_clients = clients.anthropic_client
        self.openai_models = self.config.get("openai_models", {})
        self.anthropic_models = self.config.get("anthropic_models", {})
        self.prompts = config.get("prompts", {})
        self.logger = logger
        self.menubar = QMenuBar(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("myLLM")
        self.setGeometry(100, 100, 800, 950)

        main_layout = QVBoxLayout(self)
        self.menubar = QMenuBar(self)
        main_layout.setMenuBar(self.menubar)
        
        self.setup_menu()
        self.setup_prompt_buttons(main_layout)
        self.setup_text_inputs(main_layout)
        self.setup_model_selection(main_layout)
        self.setup_action_buttons(main_layout)
        self.setup_progress_bar(main_layout)
        self.setup_output_area(main_layout)
        
        self.setLayout(main_layout)
        self.setup_shortcuts()
        self.check_configuration()

        self.text_area.setFocus()

    def setup_menu(self):
        prompt_menu = QMenu("Prompts", self)
        self.menubar.addMenu(prompt_menu)
        if self.prompts:
            for prompt_name, prompt_text in self.prompts.items():
                action = prompt_menu.addAction(prompt_name)
                action.triggered.connect(lambda checked=False, p=prompt_text: self.insert_prompt(p))

    def setup_prompt_buttons(self, layout):
        main_layout = QVBoxLayout()
        
        self.setup_menu()
        self.setup_prompt_buttons(main_layout)
        self.setup_text_inputs(main_layout)
        self.setup_model_selection(main_layout)
        self.setup_action_buttons(main_layout)
        self.setup_progress_bar(main_layout)
        self.setup_output_area(main_layout)
        
        self.setLayout(main_layout)
        self.setup_shortcuts()
        self.check_configuration()

        self.text_area.setFocus()

    def setup_menu(self):
        prompt_menu = QMenu("Prompts", self)
        self.menubar.addMenu(prompt_menu)
        if self.prompts:
            for prompt_name, prompt_text in self.prompts.items():
                action = prompt_menu.addAction(prompt_name)
                action.triggered.connect(lambda checked=False, p=prompt_text: self.insert_prompt(p))

    def setup_prompt_buttons(self, layout):
        if self.prompts:
            preset_layout = QHBoxLayout()
            for i, (prompt_name, prompt_text) in enumerate(self.prompts.items()):
                if i > 4:
                    break
                button = self.create_prompt_button(prompt_name, prompt_text, i)
                preset_layout.addWidget(button)
            layout.addLayout(preset_layout)

    def create_prompt_button(self, prompt_name, prompt_text, index):
        button = QPushButton(prompt_name, self)
        prompt_text = f"{prompt_text} \n {deliminator} \n"
        def on_button_clicked(checked=False, p=prompt_text):
            self.insert_prompt(p)
        button.clicked.connect(on_button_clicked)
        shortcut = QShortcut(QKeySequence(f"Ctrl+{index+1}"), self)
        shortcut.activated.connect(on_button_clicked)
        return button

    def setup_text_inputs(self, layout):
        self.text_box = QLineEdit(self, placeholderText="Claude only. Enter system here. (default: user)")
        layout.addWidget(self.text_box)
        self.text_area = TextEditWithZoom(self, placeholderText="Enter your prompt here")
        layout.addWidget(self.text_area)

    def setup_model_selection(self, layout):
        model_layout = QHBoxLayout()
        self.model_group = QButtonGroup(self)

        if self.openai_models:
            self.add_model_buttons(self.openai_models, model_layout)
        if self.anthropic_models:
            self.add_model_buttons(self.anthropic_models, model_layout)

        layout.addLayout(model_layout)

        if len(self.model_group.buttons()) > 0:
            self.model_group.buttons()[0].setChecked(True)

            for i, button in enumerate(self.model_group.buttons()):
                shortcut = QShortcut(QKeySequence(f"Ctrl+Alt+{i+1}"), self)
                shortcut.activated.connect(button.click)

        
    def add_model_buttons(self, models, layout):
        for model in models.keys():
            button = QRadioButton(model, self)
            layout.addWidget(button)
            self.model_group.addButton(button)

    def setup_action_buttons(self, layout):
        button_layout = QHBoxLayout()

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.on_send)
        button_layout.addWidget(self.send_button)

        self.append_button = QPushButton("↑", self)
        self.append_button.clicked.connect(self.on_append)
        button_layout.addWidget(self.append_button)

        layout.addLayout(button_layout)

    def setup_progress_bar(self, layout):
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

    def setup_output_area(self, layout):
        self.output_area = TextEditWithZoom(self)
        layout.addWidget(self.output_area)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.on_send)
        QShortcut(QKeySequence("Meta+Return"), self).activated.connect(self.on_send)
        QShortcut(QKeySequence("Alt+Return"), self).activated.connect(self.on_append)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.text_area.clear())

    def check_configuration(self):
        if not self.config:
            self.show_error(messages.error_message_missing_config)
        elif not self.openai_clients and not self.anthropic_clients:
            self.show_error(messages.message_missing_both_keys)
        else:
            self.handle_partial_configuration()

    def show_error(self, message):
        self.output_area.setHtml(f"<font color='red'>Error: {message}</font> {messages.welcome_message}")
        self.disable_inputs()

    def handle_partial_configuration(self):
        if not self.openai_clients:
            self.output_area.setHtml(f"<font color='red'>Error: {messages.message_missing_openaikey}</font> {messages.welcome_message}")
        elif not self.anthropic_clients:
            self.output_area.setHtml(f"<font color='red'>Error: {messages.message_missing_anthropickey}</font> {messages.welcome_message}")
        elif not self.openai_models and not self.anthropic_models:
            self.show_error(messages.error_missing_models)
        elif not self.prompts:
            self.output_area.setHtml(f"<font color='red'>{messages.error_missing_prompts}</font> {messages.welcome_message}")
        else:
            self.output_area.setHtml(messages.welcome_message)

    def disable_inputs(self):
        self.send_button.setEnabled(False)
        self.append_button.setEnabled(False)
        self.text_area.setReadOnly(True)
        self.output_area.setReadOnly(True)


    def on_send(self):
        prompt = self.text_area.toPlainText()
        model_button = self.model_group.checkedButton()
        model = model_button.text() if model_button else "gpt-3.5-turbo"
        system = self.text_box.text()
        if prompt:
            self.logger.info(f"model: {model}, system: {system}, prompt: {prompt}")
            self.progress_bar.setRange(0, 0)  # indeterminate progress bar
            self.worker = Worker(prompt, model, system, self.openai_models, self.anthropic_models, self.openai_clients, self.anthropic_clients, self.logger)
            self.worker.result.connect(self.update_output)
            self.worker.start()

    def update_output(self, response):
        self.progress_bar.setRange(0, 1)  # stop progress bar
        self.output_area.setPlainText(response)
        self.logger.info(f"response: {response}")

    def on_append(self):
        original_prompt = self.text_area.toPlainText()
        response_txt = self.output_area.toPlainText()
        self.logger.debug(f"original_prompt: {original_prompt}, response_txt: {response_txt}")

        if response_txt:
            new_prompt = f"{original_prompt}\n{deliminator}\n[Model's response]: {response_txt} \n{deliminator}\n"
            self.text_area.setPlainText(new_prompt)
        
        # place the cursor at the end of the text
        cursor = self.text_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End) 
        self.text_area.setTextCursor(cursor)

    def insert_prompt(self, prompt_text):
        self.text_area.setPlainText(prompt_text)
        self.logger.debug(f"Prompt inserted: {prompt_text}")
        # auto focus on the last line
        cursor = self.text_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_area.setTextCursor(cursor)


def main():

    # Initialize the logger
    os.makedirs(log_path.parent, exist_ok=True)
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    sh = StreamHandler()
    fh = RotatingFileHandler(
        log_path, maxBytes=1000000, backupCount=5, encoding="utf-8"
        )
    sh.setLevel(INFO)
    fh.setLevel(INFO)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    fh.setFormatter(formatter)  # Add this line to set the formatter
    logger.addHandler(sh)
    logger.addHandler(fh)

    logger.info("App started")

    config = load_config(json_path, logger)

    clients = model_clients(logger)
    clients.get_model_clients()

    app = QApplication(sys.argv)
    chatgpt_app = GPTApp(config, clients, logger)

    chatgpt_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
