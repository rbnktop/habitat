import sys
import signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QTimer
from gui import SplashScreen, HubView, ToolsContainer
from logic import RabbitLogic

class AppController:
    """Central controller for FaunaKit Hub app.
    
    Manages splash, hub, tools windows, connects UI signals to logic,
    handles phase flows for Fuzzy Rabbit tool.
    
    Attributes:
        app (QApplication): Qt app instance.
        logic (RabbitLogic): Business logic engine.
        hub_window (QMainWindow): Hub view window.
        tools_window (ToolsContainer): Tools window.
        timer (QTimer): Keeps app responsive for signals.
        splash (SplashScreen): Startup splash.
    """
    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        self.app = QApplication(sys.argv)
        self.logic = RabbitLogic()
        self.hub_window = None
        self.tools_window = None

        self.timer = QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(lambda: None)

        self.splash = SplashScreen("logo.png")
        self.splash.show()
        QTimer.singleShot(1500, self.show_hub)

    def show_hub(self):
        """Create and show hub window, connect launch signal."""
        self.hub_window = QMainWindow()
        self.hub_window.setWindowTitle("FaunaKit Hub")
        self.hub_window.resize(400, 300)
        
        hub_content = HubView()
        hub_content.launch_tools_signal.connect(self.open_tools)
        
        self.hub_window.setCentralWidget(hub_content)
        self.splash.finish(self.hub_window)
        self.hub_window.show()

    def open_tools(self):
        """Open tools window if not exists, connect all signals, raise."""
        if self.tools_window is None:
            self.tools_window = ToolsContainer()
            # Connect phase signals
            self.tools_window.fuzzy_view.phase1.start_matching_signal.connect(self.handle_phase1_start)
            self.tools_window.fuzzy_view.phase2.confirm_signal.connect(self.handle_phase2_confirm)
            self.tools_window.fuzzy_view.closed.connect(self.close_tools)
            self.tools_window.window_closed_signal.connect(self.on_tools_destroyed)
            
        self.tools_window.show()
        self.tools_window.raise_()

    def handle_phase1_start(self, excel_path: str, raw_text: str):
        """Handle Phase1 'Check Similarities': load Excel, find matches, load Phase2, switch phase.
        
        Args:
            excel_path (str): Selected Excel file path.
            raw_text (str): Pasted/search text.
        """
        if not excel_path or not raw_text.strip():
            QMessageBox.warning(self.tools_window, "Input Error", "Please select Excel file and provide text items.")
            return

        try:
            self.logic.load_environment(excel_path)
            matches = self.logic.find_matches(raw_text)
            self.tools_window.fuzzy_view.update_result(matches)
        except Exception as e:
            QMessageBox.critical(self.tools_window, "Processing Error", f"Failed to process: {str(e)}")

    def handle_phase2_confirm(self, user_selections: dict):
        """Handle Phase2 confirm: build final data with dates, display Phase3, switch.
        
        Args:
            user_selections (dict): {original: selected_match} from cards.
        """
        final_data = []
        for original, chosen in user_selections.items():
            date = self.logic.extract_latest_date(chosen)
            final_data.append({
                "original": original,
                "match": chosen,
                "date": date
            })
        self.tools_window.fuzzy_view.phase3.display_results(final_data)
        self.tools_window.fuzzy_view.go_to_phase(2)

    def close_tools(self):
        """Hide tools on back button (not destroy)."""
        if self.tools_window:
            self.tools_window.hide()

    def on_tools_destroyed(self):
        """Cleanup tools reference on actual close."""
        self.tools_window = None

    def run(self):
        """Start Qt event loop."""
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()

