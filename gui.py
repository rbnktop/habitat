# gui.py
from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QLabel, QStackedWidget, QSplashScreen, QLineEdit)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

class SplashScreen(QSplashScreen):
    """Transparent splash screen showing only the PNG."""
    def __init__(self, image_path):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

class HubView(QWidget):
    """The landing page for the Hub."""
    launch_tools_signal = Signal() # Signal to notify controller to switch windows

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("FaunaKit Hub")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.btn_fuzzy_rabbit = QPushButton("Launch Fuzzy Rabbit")
        self.btn_fuzzy_rabbit.setFixedSize(200, 50)
        
        # Connect button to our custom signal
        self.btn_fuzzy_rabbit.clicked.connect(self.launch_tools_signal.emit)

        layout.addWidget(self.title)
        layout.addWidget(self.btn_fuzzy_rabbit)

class FuzzyRabbitView(QWidget):
    """The UI for the Fuzzy Rabbit tool."""
    submitted = Signal(str) # Emits the text when 'Run Logic' is clicked
    closed = Signal()      # Emits when 'Close' is clicked

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.back_button = QPushButton("← Back to Hub")
        self.back_button.clicked.connect(self.closed.emit)

        self.title = QLabel("Fuzzy Rabbit")
        
        # We need an actual QLineEdit to get user input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter designer notes...")
        
        self.run_button = QPushButton("Run Logic")
        self.run_button.clicked.connect(self.handle_submit)
        
        self.result_output = QLabel("Awaiting Input...")
        self.result_output.setWordWrap(True)

        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.title)
        layout.addWidget(self.input_field)
        layout.addWidget(self.run_button)
        layout.addWidget(self.result_output)

    def handle_submit(self):
        """Extracts text and emits the signal."""
        text = self.input_field.text()
        self.submitted.emit(text)

    def update_result(self, text):
        """Public method for the controller to push data back."""
        self.result_output.setText(text)

class ToolsContainer(QMainWindow):
    """
    The window that hosts different tools. 
    It emits a signal when it is being closed via 'X' or button.
    """
    window_closed_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaunaKit Tools")
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize tool views
        self.fuzzy_view = FuzzyRabbitView()
        self.stack.addWidget(self.fuzzy_view)

    def closeEvent(self, event):
        """Override the OS-level close event (the 'X' button)."""
        self.window_closed_signal.emit()
        event.accept()