import requests
# import pandas as pd
from .config import *
from .sec_api import *
from .helpers import get_CIK, process_form4s

def main():
    # --------------------------------------------------------------------------------
    # Get CIK
    cik = get_CIK(ticker=ticker, ciks_file_path=ciks_file_path, headers=headers)
    if not cik:
        print(f"CIK for ticker {ticker} not found. Please check the ticker and try again.")
        return

    print(f"CIK for ticker {ticker}: {cik}")

    # --------------------------------------------------------------------------------
    # Use CIK to get Form 4s metadata
    metadata = get_filing_metadata(cik)

    if not metadata or "filings" not in metadata or "recent" not in metadata["filings"]:
        print(f"Failed to retrieve filings metadata for CIK: {cik}")
        return

    all_forms = pd.DataFrame.from_dict(metadata["filings"]["recent"])
    form4s = all_forms[all_forms["form"] == "4"].copy()
    form4s["reportDate"] = pd.to_datetime(form4s['reportDate']).dt.date
    form4s = form4s[form4s["reportDate"] >= start_date]
    form4s["accessionNumber"] = form4s["accessionNumber"].str.replace("-", "")
    save_form4s_to_csv(ticker, form4s)

    # --------------------------------------------------------------------------------
    # Use Form 4s metadata to get Form 4s
    process_form4s(cik=cik, ticker=ticker)


if __name__ == "__main__":
    main()
