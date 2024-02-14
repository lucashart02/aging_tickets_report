from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Load the environment variables
load_dotenv()
input_file_path = os.getenv('INPUT_FILE')
output_dir = os.getenv('OUTPUT_DIR')

def apply_spc(report_open):
    # Create a pivot table that shows the count of tickets per person organized by status
    total_tickets = pd.pivot_table(report_open, values='ID', columns='Prim Resp', index='Status', aggfunc='count', fill_value=0)

    # Add a row to total tickets that is a total count of tickets for each "Prim Resp"
    total_tickets.loc['Total'] = total_tickets.sum()

    # Define a function to apply conditional formatting
    def highlight_large_ticket_counts(val):
        color = 'red' if val >= 100 else None
        return f'color: {color}'

    # Apply the styling to the pivot table
    style_total_tickets = total_tickets.style.applymap(highlight_large_ticket_counts)

    # Create another pivot table that shows the average value of "Modified Aging" per person organized by status
    ticket_avg_age = pd.pivot_table(report_open, values='Modified Aging', columns='Prim Resp', index='Status', aggfunc='mean', fill_value=0)

    # Add a row to average age that is an average value of each status for each "Prim Resp"
    ticket_avg_age.loc['Average'] = ticket_avg_age.mean()

    # Define a function to apply conditional formatting
    def highlight_large_avg_aging(val):
        color = 'red' if val >= 15 else None
        return f'color: {color}'

    # Apply the styling to the second pivot table
    style_ticket_avg_age = ticket_avg_age.style.applymap(highlight_large_avg_aging)

    # Filter rows with "Modified Aging" value of 15 or more
    detail_aging = report_open[report_open['Modified Aging'] >= 15]
    detail_aging = detail_aging.style.applymap(lambda x: 'color: red', subset=['Modified Aging'])

    return style_total_tickets, style_ticket_avg_age, detail_aging

def process_aging_report(input_file_path, output_dir):
    try:
        # Read the input Excel file into a DataFrame
        aging_report = pd.read_excel(input_file_path)

        # Perform filtering based on the 'Type' column and 'Resp Group'
        for col in aging_report.columns:
            if aging_report[col].dtype == 'object':
                aging_report[col] = aging_report[col].astype(str)

        filtered_report = aging_report[(aging_report['Type'] == 'Accounts Payable / Invoicing') & (aging_report['Resp Group'] == 'MAPS: AP Specialist')]

        # Update date columns to be in the short date format
        filtered_report.loc[:, 'Created'] = pd.to_datetime(filtered_report['Created']).dt.strftime('%Y-%m-%d')
        filtered_report.loc[:, 'Modified'] = pd.to_datetime(filtered_report['Modified']).dt.strftime('%Y-%m-%d')
        filtered_report.loc[:, 'Resolved Date'] = pd.to_datetime(filtered_report['Resolved Date']).dt.strftime('%Y-%m-%d')

        # Add columns for Aging
        filtered_report.insert(4, 'Created Aging', (pd.to_datetime('today') - pd.to_datetime(filtered_report['Created'])).dt.days)
        filtered_report.insert(5, 'Modified Aging', (pd.to_datetime('today') - pd.to_datetime(filtered_report['Modified'])).dt.days)

        # TODO: SPC
        # Filter out tickets with status "Closed"
        report_open = filtered_report[filtered_report['Status'] != 'Closed']

        style_total_tickets, style_ticket_avg_age, detail_aging = apply_spc(report_open)

        # Write the manipulated DataFrame and the styled pivot tables to a new Excel file
        output_file_path = Path(output_dir) / f'[MODIFIED]{Path(input_file_path).stem}.xlsx'

        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            # Write the filtered DataFrame to the first sheet
            filtered_report.to_excel(writer, sheet_name='Mod Aging', index=False)
            
            # Save the pivot table with conditional formatting to the second sheet
            style_total_tickets.to_excel(writer, sheet_name='Total Tickets')

            # Save the second pivot table with conditional formatting to the third sheet
            style_ticket_avg_age.to_excel(writer, sheet_name='PVT - Ticket Age Avg')

            # Save the second pivot table with conditional formatting to the third sheet
            detail_aging.to_excel(writer, sheet_name='Detail Greater than Aging')
            
        return 0
    except Exception as e:
        print(f'Failed to process the aging report: {e}')
        return 1

# Call the function to execute the script
if __name__ == "__main__":
    process_aging_report(input_file_path, output_dir)