import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from .config import headers, stocks_folder_path, transaction_map, owner_type_map

def get_filing_metadata(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)

    if (response.status_code == 200):
        return response.json()
    else:
        return None

def load_existing_form4s(file_path):
    if (not os.path.exists(stocks_folder_path)):
        os.makedirs(stocks_folder_path)
    
    if (os.path.exists(file_path)):
        return pd.read_csv(file_path, dtype={"accessionNumber": str, "Form_4_Available": bool})
    
    return None

def save_form4s_to_csv(ticker, new_form4s):
    file_path = f"{stocks_folder_path}/{ticker}.csv"
    
    new_form4s["Form_4_Available"] = False

    existing_form4s = load_existing_form4s(file_path=file_path)
    if (existing_form4s is not None):
        combined_form4s = new_form4s.merge(
            existing_form4s[["accessionNumber", "Form_4_Available"]], 
            on="accessionNumber", 
            how="left", 
            suffixes=("", "_existing")
        )
        
        combined_form4s["Form_4_Available"] = combined_form4s["Form_4_Available_existing"].fillna(combined_form4s["Form_4_Available"])
        combined_form4s = combined_form4s.drop(columns=["Form_4_Available_existing"])
        
        missing_rows = existing_form4s[~existing_form4s["accessionNumber"].isin(combined_form4s["accessionNumber"])]
        combined_form4s = pd.concat([combined_form4s, missing_rows])
    else:
        combined_form4s = new_form4s
    
    combined_form4s.to_csv(file_path, index=False)
    
    return file_path

def parse_form4_xml(cik, accession_no):
    # accession_no = accession_no.replace("-", "")
    response = requests.get(
        f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no}/form4.xml",
        headers=headers,
    )

    if (response.status_code == 404):
        # print(f"No Form 4s found with accession number: {accession_no}")
        return None
    elif (response.status_code == 200):
        root = ET.fromstring(response.content)
        # Extract general information
        try:
            insider = root.find(".//reportingOwnerId/rptOwnerName").text.strip()
        except:
            insider = None

        try:
            isDirector = root.find(".//reportingOwnerRelationship/isDirector")
            if (isDirector is not None):
                relation = "Director"
            else:
                relation = root.find(".//reportingOwnerRelationship/officerTitle").text.strip()
        except:
            relation = None

        try:
            last_date = root.find(".//transactionDate/value").text.strip()
        except:
            last_date = None

        try:
            transaction_code = root.find('.//transactionCoding/transactionCode').text.strip()
            transaction = transaction_map.get(transaction_code, "Unknown Transaction")
        except:
            transaction = None

        try:
            owner_type = root.find(".//ownershipNature/directOrIndirectOwnership/value").text.strip()
            owner_type = owner_type_map.get(owner_type, "Unknown Owner Type")
        except:
            owner_type = None

            # Form 4 specific data extraction
            shares_traded, price, shares_held = None, None, None

        try:
            # Check for non-derivative transactions
            non_derivative = root.find(".//nonDerivativeTransaction")
            if (non_derivative is not None):
                shares_traded = non_derivative.find(".//transactionAmounts/transactionShares/value").text.strip()
                price = non_derivative.find(".//transactionAmounts/transactionPricePerShare/value").text.strip()
                shares_held = non_derivative.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value").text.strip()
            
            # Check for derivative transactions
            derivative = root.find(".//derivativeTransaction")
            if (derivative is not None):
                shares_traded = derivative.find(".//transactionAmounts/transactionShares/value").text.strip()
                price = derivative.find(".//transactionAmounts/transactionPricePerShare/value").text.strip()
                shares_held = derivative.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value").text.strip()

            # Check for RSUs, Performance Shares, etc.
            rsu = root.find(".//restrictedStockUnit")
            if rsu is not None:
                shares_traded = rsu.find(".//transactionAmounts/transactionShares/value").text.strip()
                price = rsu.find(".//transactionAmounts/transactionPricePerShare/value").text.strip()
                shares_held = rsu.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value").text.strip()

            performance_shares = root.find(".//performanceShare")
            if performance_shares is not None:
                shares_traded = performance_shares.find(".//transactionAmounts/transactionShares/value").text.strip()
                price = performance_shares.find(".//transactionAmounts/transactionPricePerShare/value").text.strip()
                shares_held = performance_shares.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value").text.strip()

        except:
            shares_traded, price, shares_held = None, None, None

        return {
            "accessionNumber": accession_no,
            "Insider": insider,
            "Relation": relation,
            "Last Date": last_date,
            "Transaction": transaction,
            "Owner Type": owner_type,
            "Shares Traded": shares_traded,
            "Price": price,
            "Shares Held": shares_held
        }
    else:
        # print("Here")
        return None