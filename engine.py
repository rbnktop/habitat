import pandas as pd
from difflib import SequenceMatcher
from PySide6.QtCore import QObject, Signal

class MatchWorker(QObject):
    """
    Handles fuzzy string matching in a background thread.
    
    Attributes:
        finished (Signal): Emits the list of result dictionaries.
        progress (Signal): Emits an integer (0-100) for UI feedback.
        error (Signal): Emits an error message string if a failure occurs.
    """
    finished = Signal(list)
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, text_path, sheet_path, threshold=0.8):
        super().__init__()
        self.text_path = text_path
        self.sheet_path = sheet_path
        self.threshold = threshold

    def run(self):
        """Executes the matching logic using a right-to-left columnar priority."""
        try:
            df = pd.read_excel(self.sheet_path)
            with open(self.text_path, 'r', encoding='utf-8') as f:
                targets = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.error.emit(f"Data Load Error: {str(e)}")
            return

        reversed_cols = list(df.columns)[::-1]
        final_matches = []
        total_items = len(targets)

        for index, target in enumerate(targets):
            match_found = False
            for col in reversed_cols:
                if match_found:
                    break
                
                # Prune empty cells and normalize to strings
                pool = df[col].dropna().astype(str).tolist()
                for candidate in pool:
                    score = SequenceMatcher(None, target, candidate).ratio()
                    if score >= self.threshold:
                        final_matches.append({
                            'Item': target,
                            'Match': candidate,
                            'Date': str(col),
                            'Score': f"{round(score * 100)}%"
                        })
                        match_found = True
                        break
            
            self.progress.emit(int(((index + 1) / total_items) * 100))

        self.finished.emit(final_matches)
