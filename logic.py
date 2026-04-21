import pandas as pd
from difflib import SequenceMatcher
from dataclasses import dataclass
from typing import List, Optional

# ==========================================
# 1. DATA MODELS
# ==========================================

@dataclass
class MatchCandidate:
    """Represents a single similarity match candidate from the Excel pool.
    
    Args:
        suggested (str): The matching string from Excel.
        score (float): Similarity score (0.0 - 1.0).
    """
    suggested: str
    score: float

@dataclass
class MultiMatchResult:
    """Result for one original item: original text and top candidates.
    
    Args:
        original (str): User's input item.
        candidates (list[MatchCandidate]): Top 3 matches.
    """
    original: str
    candidates: List[MatchCandidate]

# ==========================================
# 2. CORE LOGIC ENGINE
# ==========================================

class RabbitLogic:
    """Business logic for Fuzzy Rabbit: loads Excel, performs fuzzy matching, extracts dates.
    
    Maintains state for loaded data to avoid reloading.
    
    Attributes:
        current_df (Optional[pd.DataFrame]): Loaded Excel data.
        current_pool (List[str]): Flattened unique strings for matching.
    """
    def __init__(self):
        self.current_df: Optional[pd.DataFrame] = None
        self.current_pool: List[str] = []

    def load_environment(self, excel_path: str) -> bool:
        """Load Excel file: dates from row 0, data from row 1+, flatten data pool.
        
        Args:
            excel_path (str): Path to .xlsx file.
        
        Returns:
            bool: True if loaded successfully.
        
        Raises:
            ValueError: If file invalid.
        """
        try:
            df = pd.read_excel(excel_path)
            if len(df) == 0:
                raise ValueError("Empty Excel file")
            self.dates_row = [str(x) if pd.notna(x) else '' for x in df.iloc[0].values]
            data_df = df.iloc[1:].reset_index(drop=True)
            self.current_df = data_df
            raw_values = pd.unique(data_df.values.ravel())
            self.current_pool = [str(x).strip().lower() for x in raw_values if pd.notna(x) and str(x).strip()]
            return True
        except Exception as e:
            raise ValueError(f"Failed to load Excel: {str(e)}")


    def _parse_input_text(self, raw_text: str) -> List[str]:
        """Split multi-line text to list of items to match.
        
        Args:
            raw_text (str): User input text.
        
        Returns:
            List[str]: Cleaned list of search terms.
        """
        return [line.strip() for line in raw_text.splitlines() if line.strip()]

    def _get_similarity(self, search_term: str, pool_item: str) -> float:
        """Compute string similarity ratio.
        
        Args:
            search_term (str): User item.
            pool_item (str): Excel item.
        
        Returns:
            float: 0.0 (no match) to 1.0 (exact).
        """
        search = search_term.lower().strip()
        target = pool_item.lower().strip()
        return SequenceMatcher(None, search, target).ratio()

    def find_matches(self, raw_search_text: str, threshold: float = 0.4) -> List[MultiMatchResult]:
        """Find top 3 matches for each search item.
        
        Args:
            raw_search_text (str): Multi-line user text.
            threshold (float): Min score to consider.
        
        Returns:
            List[MultiMatchResult]: Matches for each item.
        
        Raises:
            RuntimeError: If no data loaded.
        """
        if not self.current_pool:
            raise RuntimeError("No Excel data loaded. Call load_environment first.")

        search_items = self._parse_input_text(raw_search_text)
        results = []

        for item in search_items:
            candidates = []
            for pool_item in self.current_pool:
                score = self._get_similarity(item, pool_item)
                if score >= threshold:
                    candidates.append(MatchCandidate(pool_item.capitalize(), score))  # Capitalize for display
            
            candidates.sort(key=lambda x: x.score, reverse=True)
            results.append(MultiMatchResult(item, candidates[:3]))

        return results

    def extract_latest_date(self, match_value: str) -> str:
        """Extract date from row 0 of column where match appears (rightmost if multiple).
        
        Args:
            match_value (str): Confirmed match string.
        
        Returns:
            str: Date or 'No date found'.
        """
        if not match_value or match_value == "NONE" or self.current_df is None or not hasattr(self, 'dates_row'):
            return "No date found"

        match_str = str(match_value).strip()
        num_cols = len(self.current_df.columns)
        matching_cols = []

        for col_idx in range(num_cols):
            col_name = self.current_df.columns[col_idx]
            column_data = self.current_df[col_name].astype(str).str.strip()
            if column_data.eq(match_str).any():
                matching_cols.append(col_idx)

        if matching_cols:
            # Pick rightmost ('latest') column
            latest_col = max(matching_cols)
            date_val = self.dates_row[latest_col]
            return date_val if date_val else "No date"
        
        return "No date found"


