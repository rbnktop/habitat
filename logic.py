import pandas as pd
from difflib import SequenceMatcher
from dataclasses import dataclass
from typing import List, Optional


def get_latest_item_matches(text_filepath, spreadsheet_path, threshold=0.8):
    """
    Performs fuzzy matching between a list of strings and a columnar spreadsheet.
    Prioritizes the rightmost columns to extract the most recent occurrences.
    """
    # Initialize data structures
    try:
        df = pd.read_excel(spreadsheet_path)
        with open(text_filepath, 'r', encoding='utf-8') as f:
            search_items = [line.strip() for line in f if line.strip()]
    except Exception as e:
        return f"File I/O Error: {e}"

    # Reverse columns to process most recent dates first
    recent_first_columns = list(df.columns)[::-1]
    final_matches = []

    for target in search_items:
        match_found = False
        
        for date_col in recent_first_columns:
            if match_found:
                break
                
            # Clean column data: remove nulls and normalize to strings
            candidates = df[date_col].dropna().astype(str).tolist()
            
            for candidate in candidates:
                # SequenceMatcher utilizes the Gestalt Pattern Matching algorithm
                similarity = SequenceMatcher(None, target, candidate).ratio()
                
                if similarity >= threshold:
                    final_matches.append({
                        'item': target,
                        'match': candidate,
                        'date': str(date_col),
                        'score': round(similarity, 3)
                    })
                    # Exit the column loop for this specific item
                    match_found = True
                    break 
                    
    return final_matches

# Example Execution
# results = get_latest_item_matches('input.txt', 'data.xlsx', threshold=0.85)
