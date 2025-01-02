import subprocess
from merge_clean_upload import merge_and_clean_csv_files, upload_to_google_sheets

# Define the directory paths and Google Sheet name
csv_dir = "data_files"
output_dir = "data_files"
sheet_name = "iphone_scrape"
credentials_path = "service_account.json"

scrapers = [
    "euronics.py",
    "elisa.py",
    "onoff.py",
    "klick.py"
]


def run_scrapers():

    print("Running scraper scripts...")
    for scraper in scrapers:
        try:
            print(f"Running {scraper}...")
            subprocess.run(["python", scraper], check=True)
            print(f"{scraper} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running {scraper}: {e}")
            continue
    print("All scraper scripts completed.")


def main():

    run_scrapers()

    # Merge and clean the CSV files
    final_file = merge_and_clean_csv_files(csv_dir, output_dir)
    print(f"CSV merge and cleaning completed. Final file: {final_file}")

    # Upload the merged data to Google Sheets
    upload_to_google_sheets(final_file, sheet_name, credentials_path)
    print("Upload to Google Sheets completed.")


if __name__ == "__main__":
    main()
