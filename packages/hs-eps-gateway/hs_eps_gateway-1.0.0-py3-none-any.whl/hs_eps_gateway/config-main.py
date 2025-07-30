import os

# Is in debug
DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"

# EPS Gateway Configuration with Environment Variable Priority
MERCHANT_ID = os.getenv("EPS_MERCHANT_ID", "29e86e70-0ac6-45eb-ba04-9fcb0aaed12a")
STORE_ID = os.getenv("EPS_STORE_ID", "d44e705f-9e3a-41de-98b1-1674631637da")
USERNAME = os.getenv("EPS_USERNAME", "Epsdemo@gmail.com")
PASSWORD = os.getenv("EPS_PASSWORD", "Epsdemo258@")
HASH_KEY = os.getenv("EPS_HASH_KEY", "FHZxyzeps56789gfhg678ygu876o=")

# EPS API Endpoints
TOKEN_URL = os.getenv("EPS_TOKEN_URL", "https://sandboxpgapi.eps.com.bd/v1/Auth/GetToken")
INIT_PAYMENT_URL = os.getenv("EPS_INIT_PAYMENT_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/InitializeEPS")
VERIFY_URL = os.getenv("EPS_VERIFY_URL", "https://sandboxpgapi.eps.com.bd/v1/EPSEngine/CheckMerchantTransactionStatus")
