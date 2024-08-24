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
from pathlib import Path

json_path = 'config.json'
log_path = Path("log/llm_app.log")

deliminator = " ----- "

config_example = """
<pre>
    <code>
{
    "openai_models": {
        "GPT3.5":"gpt-3.5-turbo",
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3 Sonnet": "claude-3-sonnet-20240229",
        "Claude3.5 Sonnet": "claude-3-5-sonnet-20240620"
    },
    "prompts": {
        "Default": "This is a default prompt."
        "J2E":"Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
    }
}
</code>
    </pre>

"""

message_missing_openaikey = """

<h2>WARNING: OpenAI API Key is missing.</h2>

<ol type="1">
    <li>Get your API key from https://platform.openai.com/account/api-keys</li>
    <li>Set the API key as an environment variable.</li>
</ol>

<h3>MacOS/Linux:</h3>
in your terminal, run the following command:
<pre><code>
export OPENAI_API_KEY="your-api-key"
</code></pre>

<h3>Windows:</h3>
open environment variables and add a new user variable called OPENAI_API_KEY with your API key as the value.
"""

message_missing_anthropickey = """
<h2>WARNING: Anthropic API Key is missing.</h2>

<ol type="1">
    <li>Get your API key from https://console.anthropic.com/settings/keys</li>
    <li>Set the API key as an environment variable.</li>

<h3>MacOS/Linux:</h3>
in your terminal, run the following command:

<pre><code>
export ANTHROPIC_API_KEY="your-api-key"
</code></pre>

<h3>Windows:</h3>
open environment variables and add a new user variable called ANTHROPIC_API
"""

message_missing_both_keys = """
<h1>FATAL ERROR: Both OpenAI and Anthropic API keys are missing. Set the OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables.</h1>

<ol type="1">

    <li>Get your API keys from:
        <ul>
            <li>OpenAI: https://platform.openai.com/account/api-keys</li>
            <li>Anthropic: https://app.anthropic.com/account/api-keys</li>
        </ul>
    </li>

    <li>Set the API keys as environment variables.
        <ul>
            <li>MacOS/Linux:
                <p>in your terminal, run the following commands:</p>
                <p>export OPENAI_API_KEY="your-openai-api-key"</p>
                <p>export ANTHROPIC_API_KEY="your-anthropic-api-key"</p>
            </li>
            <li>Windows:
                <p>open environment variables and add new user variables called OPENAI_API_KEY and ANTHROPIC_API_KEY with your API keys as the values.</p>
            </li>
        </ul>
        """


error_message_missing_config = """
<p>Conifg.json file is missing or corrupted. Place the config.json file in the same directory as the app.
See github.com/uegamiw/myLLM for more information.</p>

Following is the example of the config.json file:
""" + config_example

error_missing_prompts = """
<h1>ERROR: No prompts found in the config.json file.</h1>

<p>Place the prompt templates in the config.json file. See the example below:</p>
""" + config_example

error_missing_models = """
<h1>ERROR: No models found in the config.json file.</h1>
<p>Place the model names and IDs in the config.json file. See the example below:</p>
""" + config_example


welcome_message = """
<h1> Welcome to myLLM! </h1>
<h2> How to use</h2>
<ol type="1">
    <li> (optional) Select a prompt template from the buttons above.</li>
    <li> Enter your prompt in the text area.</li>
    <li> Select a model from the radio buttons.</li>
    <li> Click the 'Send' button or press 'Ctrl+Return' to generate a response.</li>
    <li> The response will be displayed in the output area.</li>
    <li> Click the 'Append' button or press 'Alt+Return' to append the response to the prompt.</li>
</ol>


<h2> config.json </h2>
You can customize the models and prompts by editing the config.json file. <br>
Keep the config.json file in the same directory as the app.

<h2> Logging </h2>
The app logs and all input/responses are saved in the log directory. Check the log file for more information. <br>

Author: Wataru Uegami, MD PhD (wuegami@gmail.com)
"""


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

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("myLLM")
        self.setGeometry(100, 100, 800, 950)

        main_layout = QVBoxLayout()
        preset_layout = QHBoxLayout()

        # Prompt shortcuts buttons
        if self.prompts:
            for prompt_name, prompt_text in self.prompts.items():
                self.logger.debug(f"Prompt loaded: {prompt_name}")
                prompt_text = f"{prompt_text} \n {deliminator} \n"
                self.logger.debug(f"Prompt text: {prompt_text}")

                button = QPushButton(prompt_name, self)

                # button.clicked.connect(lambda p=prompt_text: self.insert_prompt(p))
                def on_button_clicked(checked=False, p=prompt_text):
                    self.insert_prompt(p)
                # button.clicked.connect(lambda checked, p=prompt_text: self.insert_prompt(p))
                button.clicked.connect(on_button_clicked)

                preset_layout.addWidget(button)

        else:
            self.logger.error("No prompts found in the config.json file")

        main_layout.addLayout(preset_layout)

        # text box (system)
        self.text_box = QLineEdit(self, placeholderText="Claude only. Enter system here. (default: user)")
        main_layout.addWidget(self.text_box)
        
        # Input area for the prompt
        self.text_area = QTextEdit(self, placeholderText="Enter your prompt here")
        main_layout.addWidget(self.text_area)

        # Radio buttons for model selection
        self.model_group = QButtonGroup(self)
        model_layout = QHBoxLayout()
        
        if self.openai_clients is not None:
            for openai_model in self.openai_models.keys():
                self.logger.info(f"OpenAI model loaded: {openai_model}")
                openai_button = QRadioButton(openai_model, self)
                model_layout.addWidget(openai_button)
                self.model_group.addButton(openai_button)

        if self.anthropic_clients is not None:
            for anthropic_model in self.anthropic_models.keys():
                self.logger.info(f"Anthropic model loaded: {anthropic_model}")
                anthropic_button = QRadioButton(anthropic_model, self)
                model_layout.addWidget(anthropic_button)
                self.model_group.addButton(anthropic_button)

        main_layout.addLayout(model_layout)

        # preset the default model
        if len(self.model_group.buttons()) > 0:
            self.model_group.buttons()[0].setChecked(True)

        # button layout
        button_layout = QHBoxLayout()

        # Send button
        self.send_button = QPushButton("Send (Cmd+Enter)", self)
        self.send_button.clicked.connect(self.on_send)
        button_layout.addWidget(self.send_button)

        # Append button
        self.append_button = QPushButton("Append (Alt+Enter)", self)
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

        # Shortcut keybind
        ## Send button
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.on_send)
        
        mac_shortcut = QShortcut(QKeySequence("Meta+Return"), self)
        mac_shortcut.activated.connect(self.on_send)

        ## Apped button (Alt+Return)
        shortcut2 = QShortcut(QKeySequence("Alt+Return"), self)
        shortcut2.activated.connect(self.on_append)

        def disable_buttons():
            self.send_button.setEnabled(False)
            self.append_button.setEnabled(False)
            self.text_area.setReadOnly(True)
            self.output_area.setReadOnly(True)
        
        
        if not self.config:
            self.output_area.setHtml(f"<font color='red'>Error: {error_message_missing_config}</font>")
            disable_buttons()

        elif (not self.openai_clients) and (not self.anthropic_clients):
            self.output_area.setHtml(f"<font color='red'>Error: {message_missing_both_keys}</font>")
            disable_buttons()

        else:
            if not self.openai_clients:
                self.output_area.setHtml(f"<font color='red'>Error: {message_missing_openaikey}</font>")
            
            elif not self.anthropic_clients:
                self.output_area.setHtml(f"<font color='red'>Error: {message_missing_anthropickey}</font>")
            
            elif not self.openai_models and not self.anthropic_models:
                self.output_area.setHtml(f"<font color='red'>{error_missing_models}</font>")
                disable_buttons()
            
            elif not self.prompts:
                self.output_area.setHtml(f"<font color='red'>{error_missing_prompts}</font>")
            
            else:
                self.output_area.setHtml(welcome_message)

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
