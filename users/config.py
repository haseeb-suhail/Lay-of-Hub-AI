import os
from dotenv import load_dotenv
from datetime import datetime

# ------------------------------------------------------------------------------------------
# User configurations
# ------------------------------------------------------------------------------------------
ticker = 'GOOGL'
num_months_timeframes = [3, 12]     # Previous no of months' data to be displayed
# ---------------------------------------------
# Instead of using 01 we use 1, this is important
start_date = datetime(2022, 1, 1).date()       # YYYY - M - D
# end_date = datetime(2024, 25, 8).date()
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
load_dotenv()

# Global Variables
identifier = os.getenv("EMAIL_ADDRESS")
headers = {
    "User-Agent": identifier
}
# ---------------------------------------------
ciks_file_path = "./data/all_CIKs.csv"
stocks_folder_path = "./data/stock_data"
# ---------------------------------------------
transaction_map = {
    "P": "Purchase",
    "S": "Sale",
    "D": "Disposition (Non Open Market)",
    "A": "Award/Acquisition (Non Open Market)",
    "G": "Gift",
    "F": "Payment of Exercise Price or Tax Liability",
    "I": "Discretionary Transaction",
    "M": "Exercise or Conversion of Derivative Security",
    "X": "Exercise of In-the-Money or Same-Day Sale",
    "C": "Conversion",
    "L": "Small Acquisition",
    "U": "Disposition Pursuant to a Tender of Shares",
    "V": "Transaction Voluntarily Reported Earlier",
    "W": "Acquisition or Disposition by Will or the Laws of Descent and Distribution",
    "Z": "Combination of Code F and Code S",
}
owner_type_map = {
    "D": "Direct",
    "I": "Indirect"
}