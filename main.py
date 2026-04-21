# main.py
import sys
import signal
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from gui import SplashScreen, HubView, ToolsContainer
from logic import RabbitLogic

class AppController:
    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        self.app = QApplication(sys.argv)
        self.logic = RabbitLogic()
        
        self.hub_window = None
        self.tools_window = None

        # 3. The "Heartbeat" Timer
        # This keeps the Python interpreter active enough to catch signals
        self.timer = QTimer()
        self.timer.start(500) 
        self.timer.timeout.connect(lambda: None) 

        self.splash = SplashScreen("logo.png")
        self.splash.show()
        
        QTimer.singleShot(1000, self.show_hub)

    def show_hub(self):
        """Initializes and displays the main Hub."""
        self.hub_window = QMainWindow() 
        self.hub_window.setWindowTitle("FaunaKit Hub")
        self.hub_window.resize(400, 300)
        
        hub_content = HubView()
        # Connect: View Signal -> Controller Method
        hub_content.launch_tools_signal.connect(self.open_tools)
        
        self.hub_window.setCentralWidget(hub_content)
        self.splash.finish(self.hub_window)
        self.hub_window.show()

    def open_tools(self):
        """Creates the tool window if it doesn't exist."""
        if self.tools_window is None:
            self.tools_window = ToolsContainer()
            
            # Connect tool logic signals
            self.tools_window.fuzzy_view.submitted.connect(self.process_rabbit)
            self.tools_window.fuzzy_view.closed.connect(self.close_tools)
            
            # Connect the window-level close (the 'X' button)
            self.tools_window.window_closed_signal.connect(self.on_tools_destroyed)
            
        self.tools_window.show()
        self.tools_window.raise_()

    def process_rabbit(self, user_text):
        """The bridge between UI data and Logic processing."""
        result = self.logic.process_data(user_text)
        self.tools_window.fuzzy_view.update_result(result)

    def close_tools(self):
        """Triggered by the 'Back to Hub' button."""
        if self.tools_window:
            self.tools_window.close()

    def on_tools_destroyed(self):
        """Cleanup reference when the window is actually closed."""
        self.tools_window = None

    def run(self):
        # Using sys.exit ensures the OS knows the app closed correctly
        sys.exit(self.app.exec())

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()