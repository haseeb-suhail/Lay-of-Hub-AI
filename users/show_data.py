import os
import pandas as pd
from .config import *
from tabulate import tabulate
from datetime import datetime
from dateutil.relativedelta import relativedelta


def display_data(ticker):
    ticker_file_path = f"{stocks_folder_path}/{ticker}.csv"
    form4s_file_path = f"{stocks_folder_path}/{ticker}_form4_details.csv"

    if not os.path.exists(ciks_file_path):
        print("CIK file not found!")
        return

    if not os.path.exists(ticker_file_path):
        print("Ticker file not found!")
        return

    if not os.path.exists(form4s_file_path):
        print("Form 4s file not found!")
        return

    ticker_df = pd.read_csv(ticker_file_path, dtype={"accessionNumber": str}, parse_dates=["reportDate"])
    ticker_df["reportDate"] = ticker_df["reportDate"].dt.date
    form4s_df = pd.read_csv(form4s_file_path)

    for num_months in num_months_timeframes:
        print("Timeframe of ", num_months)
        cutoff_date = (datetime.today() - relativedelta(months=num_months)).date()
        ticker_df = ticker_df[ticker_df["reportDate"] >= cutoff_date]

        accession_nos = ticker_df["accessionNumber"].tolist()
        form4s_df["accessionNumber"] = form4s_df["accessionNumber"].astype(str).str.zfill(18)

        form4s_df = form4s_df[form4s_df["accessionNumber"].isin(accession_nos)]

        print(tabulate(form4s_df, headers='keys', tablefmt='pretty'))
        print("\n\n\n")


display_data(ticker=ticker)
