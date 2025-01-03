# Data Collection and Automation Pipeline

## Overview
This project automates the collection of iPhone sales listings data from local retailers websites and uploads it to a Google Sheets document. The pipeline runs daily via GitHub Actions, ensuring consistent and reliable data collection for future analysis. The ultimate goal is to gather a robust dataset to analyze trends and patterns in the data.

### Key Features
- Automated daily data collection scheduled via GitHub Actions.
- Data merging, cleaning, and uploading to Google Sheets.
- Scalable and ready for future data analysis.

---


### Software 
- **Python**: Version 3.11
- **Git**
- **Google Cloud**
- **Google Sheets**

### Libraries (from `requirements.txt`)
- pandas
- selenium
- gspread
- google-api-python-client
- google-auth
- google-auth-oauthlib
- google-auth-httplib2

### Accounts
- A Google Cloud account with access to create and manage service accounts.

---

## Workflow Description

### Pipeline Workflow
The workflow is automated using GitHub Actions and runs as follows:
1. **Scrape data**
   - **`elisa.py`**: Scrapes iPhone sales data from _**Elisa**_ and stores it into csv.
   - **`euronics.py`**: Scrapes iPhone sales data from _**Euronics**_ and stores it into csv.
   - **`klick.py`**: Scrapes iPhone sales data from _**Klick**_ and stores it into csv.
   - **`onoff.py`**: Scrapes iPhone sales data from _**OnOff**_ and stores it into csv.
2. **Merge, clean and upload data**
   -  **`merge_clean_upload.py`**: 
      - Merges all the scraped CSVs into a single dataset, named with the current date. 
      - Cleans the dataset to remove duplicates, if they exist.
      - Automatically uploads the cleaned dataset to an existing Google Sheets worksheet.
      - Applies the style and formatting of the initial Main sheet, including a formula to display product images automatically.
3. **Orchestrate all**
      - **`main.py`**: Orchestrates all the scripts to run.  
4. **Outcome**
      - The cleaned and processed data is appended to a Google Sheets file with proper formatting.
      - The Google Sheets file includes columns such as _Image URL, Product Name, Original Price, Discount Price, Product URL, Availability_, and _Seller_.
### Automation
This Pipeline uses a _**Google Cloud**_ service account to upload processed data to Google Sheets. A `_service_account.json_` file is created to store the credentials for the service account and is treated as a GitHub Action secret `(SERVICE_ACCOUNT_JSON)` for security reasons. The pipeline is configured in GitHub Actions to execute daily at 1 AM, ensuring automated and secure data collection, merging, cleaning, and uploading processes.

---


## Contact
For any questions or collaboration opportunities, please reach out:
- **Name**: Riccardo Kiho
- **Email**: riccardokiho05@gmail.com
- **Web**: www.ridigitalhub.com
- **GitHub**: [My GitHub Profile](https://github.com/LeivaLinnase)

