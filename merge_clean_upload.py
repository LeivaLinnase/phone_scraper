import os
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


credentials_path = 'service_account.json'


def merge_and_clean_csv_files(csv_dir, output_dir):
    csv_files = [file for file in os.listdir(csv_dir) if file.endswith('.csv') and "-" not in file]
    dataframes = []

    for file in csv_files:
        filepath = os.path.join(csv_dir, file)
        print(f"Reading file: {filepath}")
        df = pd.read_csv(filepath)
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.drop_duplicates(inplace=True)

    price_columns = [col for col in merged_df.columns if 'price' in col.lower()]
    for col in price_columns:
        print(f"Cleaning and formatting column: {col}")
        merged_df[col] = (
            merged_df[col]
            .astype(str)  # Ensure all values are strings
            .str.replace(r'[$€]', '', regex=True)  # Remove $ and € symbols
            .str.replace(r',', '.', regex=True)  # Replace commas with dots
            .apply(pd.to_numeric, errors='coerce')  # Convert to numeric, coercing errors to NaN
        )

    image_columns = [col for col in merged_df.columns if 'image' in col.lower()]
    for col in image_columns:
        merged_df[col] = merged_df[col].astype(str).apply(lambda x: f'{x}')

    # Create a timestamp for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file = f"{current_date}.csv"
    merged_filepath = os.path.join(output_dir, output_file)

    merged_df.to_csv(merged_filepath, index=False)
    print(f"Cleaned merged dataset saved to {merged_filepath}.")
    return merged_filepath


def replicate_main_sheet_format(spreadsheet_id, main_sheet_name, new_sheet_id, credentials_path):
    # Authenticate with the Sheets API
    creds = Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=creds)

    # Get the ID of the 'Main' sheet
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    main_sheet_id = next(sheet['properties']['sheetId'] for sheet in spreadsheet['sheets'] if sheet['properties']['title'] == main_sheet_name)

    # Prepare the batchUpdate request to copy formatting from the Main sheet to the new sheet
    requests = [
        {
            "copyPaste": {
                "source": {
                    "sheetId": main_sheet_id
                },
                "destination": {
                    "sheetId": new_sheet_id
                },
                "pasteType": "PASTE_FORMAT"
            }
        }
    ]

    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print(f"Formatting from 'Main' sheet copied to the new sheet.")


def upload_to_google_sheets(csv_file_path, sheet_name, credentials_path):
    # Authenticate and connect to Google Sheets
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(creds)

    # Open the existing Google Sheet
    sheet = client.open(sheet_name)  # Open the existing sheet by its name
    print(f"Google Sheet '{sheet_name}' found.")

    spreadsheet_id = sheet.id

    # Create a new worksheet with the current date as its name
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        worksheet = sheet.worksheet(current_date)
        print(f"Worksheet '{current_date}' already exists. Updating it.")
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=current_date, rows="1000", cols="20")
        print(f"Worksheet '{current_date}' created.")

    # Upload the CSV data to the new worksheet
    with open(csv_file_path, 'r') as file:
        content = file.read()
        data = [row.split(',') for row in content.splitlines()]

    # Update data in the worksheet
    worksheet.update(range_name='A1', values=data)
    print(f"Data from '{csv_file_path}' uploaded to worksheet '{current_date}' in Google Sheet '{sheet_name}'.")

    # Convert image_url fields to =IMAGE() formulas
    convert_image_urls_to_images(worksheet)

    # Replicate formatting from the 'Main' sheet
    replicate_main_sheet_format(spreadsheet_id, "Main", worksheet.id, credentials_path)


def convert_image_urls_to_images(worksheet):

    all_data = worksheet.get_all_values()
    rows_with_formulas = []

    for row_idx, row in enumerate(all_data):
        new_row = []
        for col_idx, cell in enumerate(row):
            # Check if the cell ends with a valid image file extension
            if cell.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                # Replace URL with the =IMAGE() formula
                new_row.append(f'=IMAGE("{cell}")')
            else:
                new_row.append(cell)
        rows_with_formulas.append(new_row)

    # Update the worksheet with USER_ENTERED mode to interpret formulas correctly
    worksheet.update(range_name='A1', values=rows_with_formulas, value_input_option='USER_ENTERED')
    print("Image URLs converted to =IMAGE() formulas.")


if __name__ == "__main__":
    csv_dir = "data_files"
    output_dir = "data_files"
    sheet_name = "iphone_scrape"  # Name of the existing Google Sheet

    # Merge and clean CSV files
    final_file = merge_and_clean_csv_files(csv_dir, output_dir)
    print(f"CSV merge and cleaning completed. Final file: {final_file}")

    # Upload to Google Sheets
    upload_to_google_sheets(final_file, sheet_name, credentials_path)
    print("Upload to Google Sheets completed.")
