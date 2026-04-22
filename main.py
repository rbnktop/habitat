import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QThread
from interface import ToolView
from engine import MatchWorker

class AppController(QMainWindow):
    """Main controller managing the workflow and threading."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Matcher Pro")
        self.resize(800, 500)
        
        # Initialize UI Component
        self.tool_view = ToolView()
        self.setCentralWidget(self.tool_view)
        
        # Connect UI Signals
        self.tool_view.start_btn.clicked.connect(self.initiate_matching)
        
        self.thread = None
        self.worker = None

    def initiate_matching(self):
        """Prompts user for files and starts the background worker."""
        text_file, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt)")
        if not text_file: return
        
        excel_file, _ = QFileDialog.getOpenFileName(self, "Select Spreadsheet", "", "Excel Files (*.xlsx *.xls)")
        if not excel_file: return

        # Thread Setup
        self.thread = QThread()
        self.worker = MatchWorker(text_file, excel_file)
        self.worker.moveToThread(self.thread)
        
        # Signal Connections
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_matching_complete)
        self.worker.error.connect(self.on_error)
        
        # Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.tool_view.start_btn.setEnabled(False)
        self.tool_view.info_label.setText("Processing... please wait.")
        self.thread.start()

    def on_matching_complete(self, results):
        """Updates the UI once the thread finishes."""
        self.tool_view.display_results(results)
        self.tool_view.start_btn.setEnabled(True)
        self.tool_view.info_label.setText(f"Done! Found {len(results)} matches.")

    def on_error(self, message):
        """Displays error messages to the user."""
        QMessageBox.critical(self, "Error", message)
        self.tool_view.start_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppController()
    window.show()
    sys.exit(app.exec())
