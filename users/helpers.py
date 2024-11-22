# Dependencies
import os
from tqdm import tqdm
import requests
import pandas as pd
from .sec_api import load_existing_form4s, parse_form4_xml
from .config import headers, stocks_folder_path
import sys

print(sys.path)


# Function Definitions
# ----------------------------------------------------------------------------------------------
# CIK Related
def process_CIKS(ciks_file, headers):
    # If the ciks file is present...
    if os.path.exists(ciks_file):
        print("CIKs file found. Loading CIKs from file...")
        ciks_list = pd.read_csv(ciks_file)

    # If the ciks file is not present
    else:
        print("CIKs file not found. Loading CIKs from SEC API...")
        cik_response = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers
        )

        if cik_response.status_code == 200:
            ciks_list = pd.DataFrame.from_dict(cik_response.json(), orient="index")
            ciks_list.to_csv(ciks_file, index=False)
        else:
            print("Failed to fetch CIKs list. Status code:", cik_response.status_code)
            return None

    # CIK needs to be 10 digits long to make requests to SEC EDGAR API
    ciks_list["cik_str"] = ciks_list["cik_str"].astype(str).str.zfill(10)
    return ciks_list


def get_CIK(ticker, ciks_file_path, headers):
    ciks_df = process_CIKS(ciks_file=ciks_file_path, headers=headers)

    if (ciks_df is not None):
        cik = ciks_df[ciks_df["ticker"] == ticker]

        # Ticker is found
        if not cik.empty:
            return cik["cik_str"].iloc[0]

        # Ticker is not found
        else:
            print("Ticker not found.")
            return None
    else:
        print("Failed to process CIKs")
        return None


# ----------------------------------------------------------------------------------------------
# Form 4s Related
def load_existing_form4s_data(file_path):
    if not os.path.exists(stocks_folder_path):
        os.makedirs(stocks_folder_path)

    if os.path.exists(file_path):
        return pd.read_csv(file_path)

    return None


def save_form4_data(data, ticker):
    new_form4s_data = pd.DataFrame(data)
    # print(new_form4s_data)
    # print(new_form4s_data.dtypes)
    accession_nos = new_form4s_data["accessionNumber"].tolist()
    # accession_nos = [str(num).lstrip('0') for num in accession_nos]
    # print(accession_nos[0])
    # print(type(accession_nos[0]))

    ticker_file_path = f"{stocks_folder_path}/{ticker}.csv"
    # print(ticker_file_path)
    ticker_form4s = pd.read_csv(ticker_file_path, dtype={"accessionNumber": "string"})
    # print(ticker_form4s)
    # print(ticker_form4s.dtypes)
    ticker_form4s["accessionNumber"] = ticker_form4s["accessionNumber"].astype(str)
    ticker_form4s.loc[ticker_form4s["accessionNumber"].isin(accession_nos), "Form_4_Available"] = True
    # print("True: ", len(ticker_form4s[ticker_form4s["Form_4_Available"] == True]))
    # print("False: ", len(ticker_form4s[ticker_form4s["Form_4_Available"] == False]))
    ticker_form4s.to_csv(ticker_file_path, index=False)

    file_path = f"{stocks_folder_path}/{ticker}_form4_details.csv"
    existing_form4s_data = load_existing_form4s_data(file_path=file_path)

    if (existing_form4s_data is not None):
        combined_form4s_data = pd.concat([new_form4s_data, existing_form4s_data], ignore_index=True)
    else:
        combined_form4s_data = new_form4s_data

    combined_form4s_data.to_csv(file_path, index=False)
    return file_path


def process_form4s(cik, ticker):
    file_path = f"{stocks_folder_path}/{ticker}.csv"
    form4s_df = load_existing_form4s(file_path=file_path)
    form4s_df = form4s_df[form4s_df["Form_4_Available"] == False]
    form4s_found = len(form4s_df)
    if (form4s_found == 0):
        print("No new Form 4s filed. Up to date with the market")
        return
    else:
        print("New Form 4s found: ", form4s_found)

    new_form4s_data = []
    tqdm.pandas()
    for _, row in tqdm(form4s_df.iterrows(), total=len(form4s_df), desc="Processing Form 4s"):

        form4_deets = parse_form4_xml(cik=cik, accession_no=row["accessionNumber"])
        # print(form4_deets)
        if (form4_deets is not None):
            new_form4s_data.append(form4_deets)

    # print("Datatype of accessionNumber", (new_form4s_data[0]["accessionNumber"]))
    if (new_form4s_data == []):
        print("No new Form 4s fetched")
    else:
        print("Fetche Form 4s: ", len(new_form4s_data))
        save_form4_data(data=new_form4s_data, ticker=ticker)