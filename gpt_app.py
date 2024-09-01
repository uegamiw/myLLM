
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PySide6.QtGui import QShortcut, QKeySequence
import messages
from ui.menu_bar import MenuBar
from ui.prompt_button_panel import PromptButtonsPanel
from ui.prompt_input_panel import PromptInputPanel
from ui.model_selection_panel import ModelSelectionPanel
from ui.action_button_panel import ActionButtonsPanel
from ui.progress_bar import ProgressBar
from ui.output_area import OutputArea
from llm_client_worker import OpenAIWorker, AnthropicWorker
from config_manager import ConfigManager
from api_client_manager import APIClientManager
from setting import deliminator, window_title

class GPTApp(QWidget):
    def __init__(
        self, config_manager: ConfigManager, clients: APIClientManager, logger
    ):
        super().__init__()
        self.config = config_manager.config
        self.openai_clients = clients.openai_client
        self.anthropic_clients = clients.anthropic_client
        self.openai_models = self.config.get("openai_models", {})
        self.anthropic_models = self.config.get("anthropic_models", {})
        self.prompts = self.config.get("prompts", {})
        self.logger = logger

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(50, 50, 800, 950)

        main_layout = QVBoxLayout(self)

        # Menu bar
        self.menubar = MenuBar(self, self.prompts, self.logger)
        main_layout.setMenuBar(self.menubar)
        self.menubar.prompt_selected.connect(self.insert_prompt)

        # Prompt buttons
        self.prompt_buttons_panel = PromptButtonsPanel(self.prompts, self)
        self.prompt_buttons_panel.prompt_selected.connect(self.insert_prompt)
        main_layout.addWidget(self.prompt_buttons_panel)

        # Prompt input
        self.prompt_input_panel = PromptInputPanel()
        main_layout.addWidget(self.prompt_input_panel)

        # Model Selection
        self.model_selection_panel = ModelSelectionPanel(self.openai_models, self.anthropic_models)
        main_layout.addLayout(self.model_selection_panel)

        # Action buttons
        self.action_button_panel = ActionButtonsPanel()
        self.action_button_panel.send_signal.connect(self.on_send)
        self.action_button_panel.append_signal.connect(self.on_append)
        main_layout.addLayout(self.action_button_panel)

        self.progress_bar = ProgressBar(self)
        main_layout.addWidget(self.progress_bar)

        self.output_area = OutputArea(self)
        main_layout.addWidget(self.output_area)

        self.setLayout(main_layout)
        self.setup_shortcuts()
        self.check_configuration()

        self.prompt_input_panel.textarea.setFocus()
        
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.on_send)
        QShortcut(QKeySequence("Meta+Return"), self).activated.connect(self.on_send)
        QShortcut(QKeySequence("Alt+Return"), self).activated.connect(self.on_append)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(
            lambda: self.prompt_input_panel.textarea.clear()
        )

    def check_configuration(self):
        if not self.config:
            self.show_error(messages.error_message_missing_config)
        elif not self.openai_clients and not self.anthropic_clients:
            self.show_error(messages.message_missing_both_keys)
        else:
            self.handle_partial_configuration()

    def show_error(self, message):
        self.output_area.setHtml(
            f"<font color='red'>Error: {message}</font> {messages.welcome_message}"
        )
        # self.disable_inputs()

    def handle_partial_configuration(self):
        if not self.openai_clients:
            self.output_area.setHtml(
                f"<font color='red'>Error: {messages.message_missing_openaikey}</font> {messages.welcome_message}"
            )
        elif not self.anthropic_clients:
            self.output_area.setHtml(
                f"<font color='red'>Error: {messages.message_missing_anthropickey}</font> {messages.welcome_message}"
            )
        elif not self.openai_models and not self.anthropic_models:
            self.show_error(messages.error_missing_models)
        elif not self.prompts:
            self.output_area.setHtml(
                f"<font color='red'>{messages.error_missing_prompts}</font> {messages.welcome_message}"
            )
        else:
            self.output_area.setHtml(messages.welcome_message)

    def on_send(self):
        system, prompt = self.prompt_input_panel.get_text()
        selected_model = self.model_selection_panel.selected_model()

        if prompt:
            self.logger.info(f"model: {selected_model}, system: {system}, prompt: {prompt}")

            self.progress_bar.start()
            self.output_area.clear()

            if selected_model in self.openai_models.keys():
                self.action_button_panel.disable_buttons()
                self.worker = OpenAIWorker(
                    prompt,
                    self.openai_models[selected_model],
                    system,
                    self.openai_clients,
                    self.logger,
                )
            elif selected_model in self.anthropic_models.keys():
                self.action_button_panel.disable_buttons()
                self.worker = AnthropicWorker(
                    prompt,
                    self.anthropic_models[selected_model],
                    system,
                    self.anthropic_clients,
                    self.logger,
                )
            else:
                self.logger.error(f"Model not found: {selected_model}")
            
            self.worker.result.connect(self.update_output)
            self.worker.start()

    def update_output(self, response):
        self.progress_bar.stop()
        # self.output_area.is_counting_up = False

        self.output_area.set_text(response)
        self.logger.info(f"response: {response}")
        self.action_button_panel.enable_buttons()

    def on_append(self):
        _, original_prompt = self.prompt_input_panel.get_text()
        
        response_txt = self.output_area.toPlainText()

        self.logger.debug(
            f"original_prompt: {original_prompt}, response_txt: {response_txt}"
        )

        if response_txt:
            new_prompt = f"{original_prompt}\n{deliminator}\n[Model's response]: {response_txt} \n{deliminator}\n"
            self.prompt_input_panel.textarea.setPlainText(new_prompt)

        # place the cursor at the end of the text
        cursor = self.prompt_input_panel.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.prompt_input_panel.textarea.setTextCursor(cursor)

    def insert_prompt(self, prompt_text):
        self.prompt_input_panel.clear_text()
        self.prompt_input_panel.append_text(prompt_text, deliminator=None)
        self.logger.debug(f"Prompt inserted: {prompt_text}")

        # auto focus on the last line
        self.prompt_input_panel.textarea.setFocus()
        cursor = self.prompt_input_panel.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.prompt_input_panel.textarea.setTextCursor(cursor)