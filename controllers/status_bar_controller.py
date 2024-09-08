class StatusBarController:
    def __init__(self, main_window, logger):
        self.status_bar = main_window.statusBar()
        self.n_threads = 0
        self.status_bar.showMessage("Ready")
        self.logger = logger

    def update_status(self):
        if self.n_threads == 0:
            self.status_bar.showMessage("Ready")

        else:
            message = f"Waiting for {self.n_threads} response(s)..."
            self.status_bar.showMessage(message)

    def increment_threads(self):
        self.n_threads += 1
        self.update_status()

    def decrement_threads(self):
        self.n_threads -= 1
        self.update_status()


    



