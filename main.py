import sys
import time
from PySide6.QtWidgets import QApplication
from gui import SplashScreen, HubWindow, ToolsContainer
from logic import RabbitLogic

class AppController:
    """
    Manages the separate Hub and Tools windows.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.logic = RabbitLogic()
        
        # 1. Show Splash Screen
        self.splash = SplashScreen("logo.png") 
        self.splash.show()
        self.app.processEvents()
        time.sleep(1)  # Reduced for testing

        # 2. Create and show Hub Window
        self.hub_window = HubWindow()
        self.hub_window.launch_tools.connect(self.open_tools_window)

        self.splash.finish(self.hub_window)
        self.hub_window.show()

    def open_tools_window(self):
        self.tools_window = ToolsContainer(self.on_tools_close, self.execute_rabbit_logic)
        self.tools_window.show()

    def execute_rabbit_logic(self):
        if hasattr(self, 'tools_window'):
            data = self.tools_window.fuzzy_screen.input_field.text() if hasattr(self.tools_window.fuzzy_screen.input_field, 'text') else "Input Data"
            result = self.logic.process_data(data)
            self.tools_window.fuzzy_screen.result_output.setText(result)

    def on_tools_close(self):
        if hasattr(self, 'tools_window'):
            self.tools_window.close()
            # Cleanup
            if hasattr(self, 'tools_window'):
                del self.tools_window

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()

