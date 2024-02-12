from pathlib import Path
import os
from dotenv import load_dotenv
import openpyxl
from datetime import datetime

def func():
    load_dotenv()
    input_file_path = os.getenv('INPUT_FILE')
    output_dir = os.getenv('OUTPUT_DIR')

    try:
        # Load the workbook and select the active worksheet
        workbook = openpyxl.load_workbook(input_file_path)
        base_report = workbook[0]

        new_sheet = workbook.create_sheet("test sheet")
        new_sheet['A1'] = "This is a new sheet"

        # TODO: Implement the rest of the requirements here

        # Save the workbook (if modifications are made)
        output_file_path = Path(output_dir) / f'modified_{Path(input_file_path).stem}.xlsx'
        workbook.save(output_file_path)

        return 0
    except Exception as e:
        print(f'Script failed during execution: {e}')
        return 1

# Call the function to execute the script
if __name__ == "__main__":
    func()