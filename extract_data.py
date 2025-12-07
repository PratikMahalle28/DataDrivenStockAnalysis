# extract_data.py
import pandas as pd
import yaml
import os
from pathlib import Path
from glob import glob

def extract_yaml_to_csv(yaml_dir="data/yaml", output_dir="data/csv"):
    """
    Extracts data from YAML files (formatted as a list of stock records)
    and transforms it into symbol-wise CSV files.
    """
    print(f"Starting data extraction process...")
    
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    all_data = []
    
    search_pattern = os.path.join(yaml_dir, "**/*.yaml")
    yaml_files = glob(search_pattern, recursive=True)
    
    if not yaml_files:
        print(f"Error: No YAML files found in '{yaml_dir}'. Please place your dataset there.")
        return

    print(f"Found {len(yaml_files)} YAML files to process.")

    for file_path in yaml_files:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            
            # The data is a LIST of records (your provided format)
            if isinstance(data, list):
                for record in data:
                    # Map the YAML keys (e.g., 'Ticker', 'close') to the desired CSV columns (e.g., 'Symbol', 'Close')
                    row = {
                        'Symbol': record.get('Ticker'),
                        # Convert date string immediately using pandas
                        'Date': pd.to_datetime(record.get('date')), 
                        'Open': record.get('open'),
                        'High': record.get('high'),
                        'Low': record.get('low'),
                        'Close': record.get('close'),
                        'Volume': record.get('volume')
                    }
                    all_data.append(row)
            else:
                # Optional: Handle the old dictionary format if some files are different
                print(f"Warning: Skipping file {file_path} as it's not a list format.")


    # Convert all extracted data into a single DataFrame
    df_master = pd.DataFrame(all_data)
    
    if df_master.empty:
        print("No data extracted. Exiting.")
        return

    # Sort the data by Symbol and Date
    df_master = df_master.sort_values(by=['Symbol', 'Date']).reset_index(drop=True)
    
    # Save the consolidated data into separate CSV files, one for each symbol
    for symbol in df_master['Symbol'].unique():
        symbol_df = df_master[df_master['Symbol'] == symbol]
        output_path = os.path.join(output_dir, f"{symbol}.csv")
        symbol_df.to_csv(output_path, index=False)

    print(f"✅ Extracted {len(df_master)} records → {len(df_master['Symbol'].unique())} CSV files saved in {output_dir}")

if __name__ == "__main__":
    # Ensure your raw yaml dataset is placed in a folder named 'data/yaml'
    # relative to your current working directory.
    extract_yaml_to_csv()
