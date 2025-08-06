import pandas as pd
import os

def examine_excel_files():
    """Examine the Excel files to understand their structure"""
    
    # Path to Excel files
    h_file = "keys/H.xlsx"
    iv_file = "keys/IV Therap.xlsx"
    
    print("=== Examining H.xlsx ===")
    try:
        # Read all sheets from H.xlsx
        h_excel = pd.ExcelFile(h_file)
        print(f"Sheets in H.xlsx: {h_excel.sheet_names}")
        
        for sheet_name in h_excel.sheet_names:
            df = pd.read_excel(h_file, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print("First few rows:")
            print(df.head())
            print("\n" + "="*50)
            
    except Exception as e:
        print(f"Error reading H.xlsx: {e}")
    
    print("\n=== Examining IV Therap.xlsx ===")
    try:
        # Read all sheets from IV Therap.xlsx
        iv_excel = pd.ExcelFile(iv_file)
        print(f"Sheets in IV Therap.xlsx: {iv_excel.sheet_names}")
        
        for sheet_name in iv_excel.sheet_names:
            df = pd.read_excel(iv_file, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print("First few rows:")
            print(df.head())
            print("\n" + "="*50)
            
    except Exception as e:
        print(f"Error reading IV Therap.xlsx: {e}")

if __name__ == "__main__":
    examine_excel_files()
