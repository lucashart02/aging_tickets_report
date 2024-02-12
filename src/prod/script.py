from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd

# Load the environment variables
load_dotenv()
input_file_path = os.getenv('INPUT_FILE')
output_dir = os.getenv('OUTPUT_DIR')

def process_aging_report(input_file_path, output_dir):
    try:
        # Read the input Excel file into a DataFrame
        df = pd.read_excel(input_file_path)

        # Perform filtering based on the 'Type' column and 'Resp Group'
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)

        df_filtered = df[(df['Type'] == 'Accounts Payable / Invoicing') & (df['Resp Group'] == 'MAPS: AP Specialist')]

        # Update date columns to be in the short date format
        df_filtered.loc[:, 'Created'] = pd.to_datetime(df_filtered['Created']).dt.strftime('%Y-%m-%d')
        df_filtered.loc[:, 'Modified'] = pd.to_datetime(df_filtered['Modified']).dt.strftime('%Y-%m-%d')
        df_filtered.loc[:, 'Resolved Date'] = pd.to_datetime(df_filtered['Resolved Date']).dt.strftime('%Y-%m-%d')

        # Add columns for Aging
        df_filtered['Created Aging'] = (pd.to_datetime('today') - pd.to_datetime(df_filtered['Created'])).dt.days
        df_filtered['Modified Aging'] = (pd.to_datetime('today') - pd.to_datetime(df_filtered['Modified'])).dt.days

        # TODO: SPC
        
        # Write the manipulated DataFrame to a new Excel file
        output_file_path = Path(output_dir) / f'[MODIFIED]{Path(input_file_path).stem}.xlsx'
        df_filtered.to_excel(output_file_path, index=False)

        return 0
    except Exception as e:
        print(f'Failed to process the aging report: {e}')
        return 1

# Call the function to execute the script
if __name__ == "__main__":
    process_aging_report(input_file_path, output_dir)