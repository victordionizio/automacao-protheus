import pandas as pd
import os

def load_csv(filepath):
    """
    Reads the CSV file and returns a list of dictionaries.
    Expected columns: 'codigo_produto', 'novo_grtrib'
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found.")
    
    try:
        df = pd.read_csv(filepath, sep=';', dtype=str) # Assuming semi-colon for Excel CSVs often used in BR
        # Normalize headers
        df.columns = [c.lower().strip() for c in df.columns]
        
        required_cols = ['codigo_produto', 'novo_grtrib']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def save_results(data, filepath):
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, sep=';')
