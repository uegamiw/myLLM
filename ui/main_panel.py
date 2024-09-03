from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from PySide6.QtGui import QShortcut, QKeySequence
import messages
from ui.prompt_button_panel import PromptButtonsPanel
from ui.prompt_input_panel import PromptInputPanel
from ui.model_selection_panel import ModelSelectionPanel
from ui.action_button_panel import ActionButtonsPanel
from ui.output_area import OutputArea
from llm_client_worker import OpenAIWorker, AnthropicWorker
from api_client_manager import APIClientManager
from setting import deliminator, window_title, db_path, response_prefix, spacing
import database

class MainPanel(QWidget):
    def __init__(self,config, clients:APIClientManager, history_panel, logger):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.config = config

        self.openai_clients = clients.openai_client
        self.anthropic_clients = clients.anthropic_client

        self.openai_models = self.config.get("openai_models", {})
        self.anthropic_models = self.config.get("anthropic_models", {})
        self.prompts = self.config.get("prompts", {})
        self.logger = logger
        self.history_panel = history_panel

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(25, 25, 800, 950)

        # database
        self.db_manager = database.DatabaseManager(self.logger, db_path)

        # Prompt buttons
        self.prompt_buttons_panel = PromptButtonsPanel(self.prompts, self)
        self.prompt_buttons_panel.prompt_selected.connect(self.insert_prompt)
        self.layout.addWidget(self.prompt_buttons_panel)

        # Prompt input
        self.prompt_input_panel = PromptInputPanel()
        self.layout.addWidget(self.prompt_input_panel)

        # Model Selection
        self.model_selection_panel = ModelSelectionPanel(self.openai_models, self.anthropic_models, self.logger)
        self.layout.addWidget(self.model_selection_panel)

        # Action buttons
        self.action_buttons_panel = ActionButtonsPanel(self)
        self.action_buttons_panel.send_signal.connect(self.handle_send)
        self.action_buttons_panel.append_signal.connect(self.handle_append)
        self.layout.addWidget(self.action_buttons_panel)

        # Output area
        self.output_area = OutputArea()
        self.layout.addWidget(self.output_area)

        self.setup_shortcuts()
        self.check_configuration()


    def insert_prompt(self, prompt_text):
        self.prompt_input_panel.clear_text()
        self.prompt_input_panel.append_text(prompt_text, deliminator=None)
        self.logger.debug(f"Prompt inserted: {prompt_text}")

        # auto focus on the last line
        self.prompt_input_panel.textarea.setFocus()
        cursor = self.prompt_input_panel.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.prompt_input_panel.textarea.setTextCursor(cursor)

    def handle_send(self):
        self.prompt = self.prompt_input_panel.get_text()
        self.selected_model = self.model_selection_panel.selected_model()

        if self.prompt:
            self.logger.debug(f"model: {self.selected_model}, prompt: {self.prompt}")

            # self.progress_bar.start()
            self.output_area.text_edit.clear()
            self.output_area.text_edit.setHtml(messages.loading_message)

            if self.selected_model in self.openai_models.keys():
                self.action_buttons_panel.disable_buttons()
                self.worker = OpenAIWorker(
                    self.prompt,
                    self.openai_models[self.selected_model],
                    self.openai_clients,
                    self.logger,
                )
            elif self.selected_model in self.anthropic_models.keys():
                self.action_buttons_panel.disable_buttons()
                self.worker = AnthropicWorker(
                    self.prompt,
                    self.anthropic_models[self.selected_model],
                    self.anthropic_clients,
                    self.logger,
                )
            else:
                self.logger.error(f"Model not found: {self.selected_model}")
            
            self.worker.result.connect(self.update_output)
            self.worker.start()

    def handle_append(self):
        original_prompt = self.prompt_input_panel.get_text()
        
        response_txt = self.output_area.text_edit.toPlainText()

        self.logger.debug(
            f"original_prompt: {original_prompt}, response_txt: {response_txt}"
        )

        if response_txt:
            new_prompt = f"{original_prompt}\n{deliminator}\n{response_prefix} {response_txt} \n{deliminator}\n"
            self.prompt_input_panel.textarea.setPlainText(new_prompt)

        self.prompt_input_panel.textarea.setFocus()

        # place the cursor at the end of the text
        cursor = self.prompt_input_panel.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.prompt_input_panel.textarea.setTextCursor(cursor)
    

    def update_output(self, response):

        self.output_area.set_text(response)
        self.logger.debug(f"response: {response}")
        self.action_buttons_panel.enable_buttons()

        self.db_manager.insert_history(self.prompt, response, self.selected_model)
        self.history_panel.refresh_table()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.handle_send)
        QShortcut(QKeySequence("Meta+Return"), self).activated.connect(self.handle_send)
        QShortcut(QKeySequence("Alt+Return"), self).activated.connect(self.handle_append)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.clear_textboxes)
        QShortcut(QKeySequence("Ctrl+l"), self).activated.connect(self.focus_prompt_input)

    def focus_prompt_input(self):
        self.prompt_input_panel.textarea.setFocus()
        # and to move the cursor to the end of the text
        cursor = self.prompt_input_panel.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.prompt_input_panel.textarea.setTextCursor(cursor)

    def clear_textboxes(self):
        self.prompt_input_panel.clear_text()
        self.output_area.text_edit.clear()
        self.output_area.text_edit.setHtml(messages.welcome_message)

    def check_configuration(self):
        if not self.config:
            self.show_error(messages.error_message_missing_config)
        elif not self.openai_clients and not self.anthropic_clients:
            self.show_error(messages.message_missing_both_keys)
        else:
            self.handle_partial_configuration()

    def show_error(self, message):
        self.output_area.text_edit.setHtml(
            f"<font color='red'>Error: {message}</font> {messages.welcome_message}"
        )

    def handle_partial_configuration(self):
        if not self.openai_clients:
            self.output_area.text_edit.setHtml(
                f"<font color='red'>Error: {messages.message_missing_openaikey}</font> {messages.welcome_message}"
            )
        elif not self.anthropic_clients:
            self.output_area.text_edit.setHtml(
                f"<font color='red'>Error: {messages.message_missing_anthropickey}</font> {messages.welcome_message}"
            )
        elif not self.openai_models and not self.anthropic_models:
            self.show_error(messages.error_missing_models)
        elif not self.prompts:
            self.output_area.text_edit.setHtml(
                f"<font color='red'>{messages.error_missing_prompts}</font> {messages.welcome_message}"
            )
        else:
            self.output_area.text_edit.setHtml(messages.welcome_message)

