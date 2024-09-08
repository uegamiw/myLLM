from views.main_window import CenterPanel
from views.menu_bar import MenuBar
from views.history_panel import HistoryPanel
from views.right_panel import RightPanel
from PySide6.QtGui import QShortcut, QKeySequence
from utils.setting import deliminator, response_prefix, n_history, search_delay, temp_deliminator
from models.llm_client_worker import OpenAIWorker, AnthropicWorker, LLMResults
from models.api_client_manager import APIClientManager
from models.config_manager import Config
from PySide6.QtCore import QThreadPool
import utils.messages as messages
from models.database_manager import DatabaseManager
from functools import partial

from typing import List
from PySide6.QtCore import QTimer
from controllers.status_bar_controller import StatusBarController

class MainController:
    def __init__(self, c_panel: CenterPanel, menu_bar:MenuBar, hist_panel:HistoryPanel,r_panel:RightPanel, clients: APIClientManager,db:DatabaseManager, config:Config,status_bar_controller:StatusBarController, logger) -> None:
        self.c_panel = c_panel
        self.r_panel = r_panel
        self.menu_bar = menu_bar
        self.hist_panel = hist_panel
        self.db = db
        
        self.openai_clients = clients.openai_client
        self.anthropic_clients = clients.anthropic_client

        self.openai_models = config.openai_models
        self.anthropic_models = config.anthropic_models

        self.logger = logger

        # self.c_panel.prompt_buttons_panel.prompt_selected.connect(self.insert_prompt)
        self.c_panel.input_panel.prompt_buttons_panel.prompt_selected.connect(self.insert_prompt)
        self.menu_bar.prompt_selected.connect(self.insert_prompt)

        self.threadpool = QThreadPool()

        # send button
        self.r_panel.action_buttons_panel.send_signal.connect(self.handle_send)

        # append button
        self.r_panel.action_buttons_panel.append_signal.connect(self.handle_append)

        # history panel
        self.populate_table_from_db(n_history)
        self.hist_panel.table_widget.cellClicked.connect(self.on_table_item_clicked)
        self.hist_panel.table_widget.itemSelectionChanged.connect(lambda: self.on_table_item_selected(self.hist_panel.table_widget.currentRow(), 0))


        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.hist_panel_search)
        self.hist_panel.search_box.textChanged.connect(lambda: self.search_timer.start(search_delay))

        self.setup_shortcuts()

        self.status_bar_controller = status_bar_controller

        self.c_panel.input_panel.set_focus()

        self.all_models = {**self.openai_models, **self.anthropic_models}


    def insert_prompt(self, prompt_text):
        self.c_panel.input_panel.clear_text()
        self.c_panel.input_panel.append_text(prompt_text, deliminator=None)
        self.logger.debug(f"Prompt inserted: {prompt_text}")

        # auto focus on the last line
        self.c_panel.input_panel.set_focus()

    def handle_append(self):
        original_prompt: str = self.c_panel.input_panel.get_text()
        response_txt: str = self.c_panel.output_area.text_edit.toPlainText()

        if response_txt:
            new_prompt = f"{original_prompt}\n{deliminator}\n{response_prefix} {response_txt} \n{deliminator}\n"
            self.c_panel.input_panel.set_text(new_prompt)
        
        self.c_panel.input_panel.set_focus()

    def handle_send(self):
        prompt = self.c_panel.input_panel.get_text()
        model_selected = self.r_panel.model_selection_panel.model_group.checkedButton().text()
        model_real = self.all_models[model_selected]
        temperature = self.r_panel.model_selection_panel.temperature_slider.value()

        if not prompt:
            self.logger.warning("No prompt to send.")
            return
        
        self.c_panel.output_area.clear()
        self.c_panel.output_area.text_edit.setHtml(messages.loading_message)

        if model_selected in self.openai_models.keys():
            self.status_bar_controller.increment_threads()
            worker = OpenAIWorker(
                prompt,
                model_selected,
                model_real,
                self.openai_clients,
                temperature,
                self.logger
                )
        elif model_selected in self.anthropic_models.keys():
            self.status_bar_controller.increment_threads()
            worker = AnthropicWorker(
                prompt,
                model_selected,
                model_real,
                self.anthropic_clients,
                temperature,
                self.logger
                )
        else:
            self.logger.error(f"Model not found: {model_selected}")
            return
        
        worker.signals.result.connect(self.update_output)
        self.threadpool.start(worker)

    def update_output(self, result_dict:dict):
        self.status_bar_controller.decrement_threads()
        result = LLMResults(**result_dict)
        self.logger.debug(result)
        self.db.insert_history(result)
        self.hist_panel.table_widget.clearContents()
        self.hist_panel.table_widget.setRowCount(0)
        self.populate_table_from_db(n_history)
        self.set_llm_results(result_dict)
        self.c_panel.input_panel.set_focus()

    def set_llm_results(self, result:dict):
        result = LLMResults(**result)
        self.c_panel.input_panel.clear_text()
        self.c_panel.input_panel.set_text(result.prompt)
        self.r_panel.model_selection_panel.set_selected_model(result.model)
        self.c_panel.output_area.set_text(result.response)
        self.r_panel.set_temperature(result.temperature)

    def populate_table_from_db(self, num_history):
        items:List[LLMResults] = self.db.get_n_history(num_history)
        self.hist_panel.table_widget.setRowCount(len(items))

        for row, item in enumerate(items):
            # self.add_item_to_table(row, item)
            self.hist_panel.set_one_row_to_table(row, item)

        for row in range(len(items)):
            # link del action to the delete label
            item_id = items[row].id
            delete_label = self.hist_panel.table_widget.cellWidget(row, 3)
            delete_label.mousePressEvent = lambda event, id=item_id: self.on_delete_label_clicked(id)

    def populate_table_with_results(self, items):
        self.hist_panel.table_widget.clearContents()
        self.hist_panel.table_widget.setRowCount(len(items))
        for row, item in enumerate(items):
            self.hist_panel.set_one_row_to_table(row, item)

        for row in range(len(items)):
            # link del action to the delete label
            item_id = items[row].id
            delete_label = self.hist_panel.table_widget.cellWidget(row, 3)
            delete_label.mousePressEvent = partial(self.on_delete_label_clicked, item_id)

    def on_delete_label_clicked(self, id):
        self.logger.info(f"Delete item with id: {id}")
        self.db.delete_history(id)
        self.hist_panel.table_widget.clearContents()
        self.hist_panel.table_widget.setRowCount(0)
        self.populate_table_from_db(n_history)

    def on_table_item_clicked(self, row, column):
        query = self.hist_panel.table_widget.item(row, 0).text()
        response = self.hist_panel.table_widget.item(row, 1).text()
        model_date = self.hist_panel.table_widget.item(row, 2).text()
        model = model_date.split("\n")[0]
        model_name = model.split(temp_deliminator)[0]
        if temp_deliminator in model:
            temperature = int(model.split(temp_deliminator)[1])
        else:
            temperature = None

        item = {
            "prompt": query,
            "response": response,
            "model": model_name,
            'datetime': model_date.split("\n")[1],
            'temperature': temperature
        }
        self.set_llm_results(item)

    def on_table_item_selected(self, row, column):
        self.on_table_item_clicked(row, 0)

    def hist_panel_search(self):
        search_text = self.hist_panel.search_box.text()
        self.logger.debug(f"perform_search, search_text: {search_text}")
        if search_text:
            search_results = self.db.search(search_text)
            self.populate_table_with_results(search_results)
        else:
            self.populate_table_from_db(n_history)


    def setup_shortcuts(self):

        # Ctrl + F, for search box
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+f"), self.c_panel)
        self.search_shortcut.activated.connect(self.hist_panel.search_box.setFocus)
        self.search_shortcut.activated.connect(self.hist_panel.search_box.selectAll)

        # Ctrl + D, for history table widget
        self.history_shortcut = QShortcut(QKeySequence("Ctrl+d"), self.c_panel)
        self.history_shortcut.activated.connect(self.hist_panel.table_widget.setFocus)

        # Ctrl + L, for focusing on the input panel
        self.input_shortcut = QShortcut(QKeySequence("Ctrl+l"), self.c_panel)
        self.input_shortcut.activated.connect(self.c_panel.input_panel.set_focus)

        # Ctrl + 0, for resetting the input panel and output panel
        self.reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self.c_panel)
        self.reset_shortcut.activated.connect(self.c_panel.clear_textboxes)

        # Alt + Return, for appending the response to the input panel
        self.append_shortcut = QShortcut(QKeySequence("Alt+Return"), self.c_panel)
        self.append_shortcut.activated.connect(self.handle_append)

        # Ctrl + Return, for sending the prompt to the model
        self.send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.c_panel)
        self.send_shortcut.activated.connect(self.handle_send)
