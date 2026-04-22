from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView)

class ToolView(QWidget):
    """The interface where the user selects files and sees results."""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.info_label = QLabel("Select your source files to begin matching.")
        self.start_btn = QPushButton("Select Files & Run")
        
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Item", "Match", "Date", "Confidence"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.results_table)

    def display_results(self, data):
        """Populates the table with the found matches."""
        self.results_table.setRowCount(0)
        for row_idx, entry in enumerate(data):
            self.results_table.insertRow(row_idx)
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(entry['Item']))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(entry['Match']))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(entry['Date']))
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(entry['Score']))
