import os

# Is in debug
DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"

# EPS Gateway Configuration with Environment Variable Priority
MERCHANT_ID = os.getenv("EPS_MERCHANT_ID", "")
STORE_ID = os.getenv("EPS_STORE_ID", "")
USERNAME = os.getenv("EPS_USERNAME", "")
PASSWORD = os.getenv("EPS_PASSWORD", "")
HASH_KEY = os.getenv("EPS_HASH_KEY", "")

# EPS API Endpoints
TOKEN_URL = os.getenv("EPS_TOKEN_URL", "https://sandboxpgapi.eps.com.bd/v1/Auth/GetToken")
INIT_PAYMENT_URL = os.getenv("EPS_INIT_PAYMENT_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/InitializeEPS")
VERIFY_URL = os.getenv("EPS_VERIFY_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/CheckMerchantTransactionStatus")


############## Rename this file to config.py and add require credentials in env ###############