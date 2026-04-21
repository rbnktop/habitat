from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QStackedWidget, QSplashScreen, 
                               QLineEdit, QTextEdit, QFileDialog, QScrollArea, 
                               QFrame, QRadioButton, QButtonGroup, QTableWidget, 
                               QTableWidgetItem, QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

# ==========================================
# 1. CORE APP STRUCTURE (Splash & Hub)
# ==========================================

class SplashScreen(QSplashScreen):
    """Displays a transparent splash screen with a PNG logo during app startup.
    
    Args:
        image_path (str): Path to the logo PNG file.
    
    Attributes:
        None additional.
    """
    def __init__(self, image_path):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

class HubView(QWidget):
    """Landing page (hub) widget with button to launch Fuzzy Rabbit tool.
    
    Signals:
        launch_tools_signal: Emitted when 'Launch Fuzzy Rabbit' button clicked.
    """
    launch_tools_signal = Signal() 

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("FaunaKit Hub")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.btn_fuzzy_rabbit = QPushButton("Launch Fuzzy Rabbit")
        self.btn_fuzzy_rabbit.setFixedSize(200, 50)
        self.btn_fuzzy_rabbit.clicked.connect(self.launch_tools_signal.emit)

        layout.addWidget(self.title)
        layout.addWidget(self.btn_fuzzy_rabbit)

# ==========================================
# 2. FUZZY RABBIT COMPONENTS (3 Phases)
# ==========================================

class MatchCard(QFrame):
    """Expandable card for reviewing a single match in Phase 2.
    
    Displays original text, best match, and radio options for alternatives.
    
    Args:
        match_result (MultiMatchResult): Data with original and candidates.
    """
    def __init__(self, match_result):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("MatchCard")
        self.setStyleSheet("#MatchCard { border: 1px solid #ddd; border-radius: 8px; background: white; margin: 2px; }")
        self.result = match_result
        
        layout = QVBoxLayout(self)
        # Header
        header = QWidget()
        h_lay = QHBoxLayout(header)
        self.lbl_original = QLabel(f"<b>{match_result.original}</b>")
        self.lbl_match = QLabel("→ None")
        self.lbl_match.setStyleSheet("color: #2980b9; font-style: italic;")
        h_lay.addWidget(self.lbl_original)
        h_lay.addStretch()
        h_lay.addWidget(self.lbl_match)
        
        # Alternatives (Hidden initially)
        self.alt_container = QWidget()
        self.alt_lay = QVBoxLayout(self.alt_container)
        self.alt_container.setVisible(False)
        self.group = QButtonGroup(self)
        self.radio_map = {}  # value -> button
        
        self.add_option("Skip / No Match", "NONE")
        for i, cand in enumerate(match_result.candidates):
            self.add_option(f"[{int(cand.score*100)}%] {cand.suggested}", cand.suggested, (i==0 and cand.score >= 0.7))

        layout.addWidget(header)
        layout.addWidget(self.alt_container)

    def add_option(self, label: str, value: str, is_default: bool = False):
        """Add a radio button option.
        
        Args:
            label (str): Display text.
            value (str): Actual value to return.
            is_default (bool): Auto-select if True.
        """
        rb = QRadioButton(label)
        self.group.addButton(rb)
        self.alt_lay.addWidget(rb)
        self.radio_map[value] = rb
        if is_default:
            rb.setChecked(True)
            self.lbl_match.setText(f"→ {value}")
        rb.toggled.connect(lambda chk, v=value: self.lbl_match.setText(f"→ {v}") if chk else None)

    def mousePressEvent(self, event):
        """Toggle alternatives visibility on click."""
        if event.button() == Qt.LeftButton:
            self.alt_container.setVisible(not self.alt_container.isVisible())

    def get_selected_value(self) -> str:
        """Get value from currently checked radio.
        
        Returns:
            str: Selected value or 'NONE'.
        """
        checked = self.group.checkedButton()
        if checked:
            for val, rb in self.radio_map.items():
                if rb is checked:
                    return val
        return "NONE"

class Phase1Input(QWidget):
    """Phase 1: User inputs Excel path and text items to match.
    
    Signals:
        start_matching_signal (str, str): Emits (excel_path, raw_text) on 'Check Similarities'.
    """
    start_matching_signal = Signal(str, str)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.btn_excel = QPushButton("Select Excel Spreadsheet")
        self.lbl_excel = QLabel("No file selected")
        self.path_excel = ""
        
        self.btn_text = QPushButton("Select Text File")
        self.lbl_text = QLabel("No text file selected")
        self.text_in = QTextEdit()
        self.btn_go = QPushButton("Check Similarities")
        layout.addWidget(self.btn_excel)
        layout.addWidget(self.lbl_excel)
        layout.addWidget(self.btn_text)
        layout.addWidget(self.lbl_text)
        layout.addWidget(QLabel("Paste Items (or load from file):"))
        layout.addWidget(self.text_in)
        layout.addWidget(self.btn_go)
        
        self.btn_excel.clicked.connect(self.get_excel_file)
        self.btn_text.clicked.connect(self.get_text_file)
        self.btn_go.clicked.connect(self.on_go)

    def get_excel_file(self):
        """Open file dialog for Excel."""
        p, _ = QFileDialog.getOpenFileName(self, "Open Excel", "", "Excel (*.xlsx *.xls)")
        if p:
            self.path_excel = p
            self.lbl_excel.setText(p.split("/")[-1])

    def get_text_file(self):
        """Load text file into editor, show error dialog if fail."""
        p, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if p:
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_in.setPlainText(content)
                self.lbl_text.setText(p.split("/")[-1])
            except Exception as e:
                QMessageBox.warning(self, "File Error", f"Error reading file: {str(e)}")

    def on_go(self):
        """Validate and emit signal."""
        if self.path_excel and self.text_in.toPlainText().strip():
            self.start_matching_signal.emit(self.path_excel, self.text_in.toPlainText())
        else:
            QMessageBox.warning(self, "Input Error", "Please select Excel and provide text.")

class Phase2Review(QWidget):
    """Phase 2: Review and select matches with expandable cards.
    
    Signals:
        confirm_signal (dict): Emits {original: selected_value} dict on confirm.
    """
    confirm_signal = Signal(dict)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.lay = QVBoxLayout(self.content)
        self.lay.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.content)
        self.btn_done = QPushButton("Confirm All")
        layout.addWidget(QLabel("Review Matches:"))
        layout.addWidget(self.scroll)
        layout.addWidget(self.btn_done)
        self.btn_done.clicked.connect(self.send_data)
        self.cards = []

    def load(self, results):
        """Populate cards with match results.
        
        Args:
            results (list[MultiMatchResult]): List of match data.
        """
        # Clear existing cards
        for c in self.cards:
            c.setParent(None)
        self.cards = [MatchCard(r) for r in results]
        for c in self.cards:
            self.lay.addWidget(c)

    def send_data(self):
        """Emit selections dict."""
        selections = {c.result.original: c.get_selected_value() for c in self.cards}
        self.confirm_signal.emit(selections)

class Phase3Results(QWidget):
    """Phase 3: Display final results in table.
    
    Args:
        None.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Original", "Match", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def display_results(self, data: list):
        """Populate table with final data rows.
        
        Args:
            data (list[dict]): List of {'original': str, 'match': str, 'date': str}.
        """
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(row['original']))
            self.table.setItem(i, 1, QTableWidgetItem(row['match']))
            self.table.setItem(i, 2, QTableWidgetItem(row['date']))

# ==========================================
# 3. TOOL CONTAINER
# ==========================================

class FuzzyRabbitTool(QWidget):
    """Main Fuzzy Rabbit tool with stacked phases and back button.
    
    Signals:
        closed: Emitted on back to hub.
    """
    closed = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.back_btn = QPushButton("← Back to Hub")
        self.back_btn.clicked.connect(self.closed.emit)
        
        self.stack = QStackedWidget()
        self.phase1 = Phase1Input()
        self.phase2 = Phase2Review()
        self.phase3 = Phase3Results()
        
        self.stack.addWidget(self.phase1)  # Index 0
        self.stack.addWidget(self.phase2)  # 1
        self.stack.addWidget(self.phase3)  # 2
        
        layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.stack)

    def go_to_phase(self, phase_index: int):
        """Switch to phase by index (0=Phase1, 1=Phase2, 2=Phase3).
        
        Args:
            phase_index (int): Stack index.
        """
        if 0 <= phase_index <= 2:
            self.stack.setCurrentIndex(phase_index)

    def update_result(self, results):
        """Load results into Phase2 and switch to it.
        
        Args:
            results (list): Match results.
        """
        self.phase2.load(results)
        self.go_to_phase(1)

class ToolsContainer(QMainWindow):
    """Container window for tools, holds fuzzy_view for compatibility.
    
    Signals:
        window_closed_signal: Emitted on close.
    """
    window_closed_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaunaKit Tools")
        self.resize(900, 700)

        self.fuzzy_view = FuzzyRabbitTool()
        self.setCentralWidget(self.fuzzy_view)

    def closeEvent(self, event):
        self.window_closed_signal.emit()
        event.accept()

