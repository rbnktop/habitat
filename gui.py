from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QLabel, QStackedWidget, QSplashScreen)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, QSize

class SplashScreen(QSplashScreen):
    """
    A custom splash screen that only shows the PNG image.
    """
    def __init__(self, image_path):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)
        
        # Make the window frameless and the background transparent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

class HubView(QWidget):
    """
    The 'Home' screen or Tool Hub.
    """
    launch_tools_signal = Signal()
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Welcome to the Tool Hub")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.info_label = QLabel("Select a tool below to begin.")
        
        # Tool Selection Buttons
        self.btn_fuzzy_rabbit = QPushButton("Launch Fuzzy Rabbit")
        self.btn_fuzzy_rabbit.setFixedSize(200, 50)
        self.btn_fuzzy_rabbit.clicked.connect(self.launch_tools_signal.emit)

        layout.addWidget(self.title)
        layout.addWidget(self.info_label)
        layout.addSpacing(20)
        layout.addWidget(self.btn_fuzzy_rabbit)

class FuzzyRabbitView(QWidget):
    """
    The specific Tool UI.
    """
    def __init__(self, close_callback):
        super().__init__()
        layout = QVBoxLayout(self)

        self.back_button = QPushButton("← Close Tools")
        self.back_button.clicked.connect(close_callback)
        self.title = QLabel("Fuzzy Rabbit Interface")
        
        # Placeholder for input
        self.input_field = QLabel("Input Data") # Simplified
        
        self.run_button = QPushButton("Run Logic")
        self.result_output = QLabel("Awaiting Input...")

        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.title)
        layout.addWidget(self.input_field)
        layout.addWidget(self.run_button)
        layout.addWidget(self.result_output)
        # run_button connect set later via set_logic_callback

    def set_logic_callback(self, callback):
    # Only connect if you aren't planning on changing this logic 
    # multiple times during the widget's lifetime.
        self.run_button.clicked.connect(callback)

class HubWindow(QMainWindow):
    launch_tools = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Hub")
        self.resize(400, 300)
        
        hub_widget = HubView()
        hub_widget.launch_tools_signal.connect(self.launch_tools.emit)
        self.setCentralWidget(hub_widget)

class ToolsContainer(QMainWindow):
    """
    Separate window for tools using stacked widget.
    """
    def __init__(self, close_callback, logic_callback):
        super().__init__()
        self.close_callback = close_callback
        self.setWindowTitle("Tools")
        self.resize(800, 600)

        self.content_stack = QStackedWidget()
        self.setCentralWidget(self.content_stack)

        self.fuzzy_screen = FuzzyRabbitView(close_callback)
        self.fuzzy_screen.set_logic_callback(logic_callback)

        self.content_stack.addWidget(self.fuzzy_screen)
