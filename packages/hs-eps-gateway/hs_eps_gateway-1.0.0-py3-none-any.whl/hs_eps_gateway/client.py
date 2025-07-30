import requests
import json
from typing import List, Optional, Union
from . import config
from .utils import generate_hash
from .esp_types import ProductItem


class EPSClient:
    def __init__(self):
        # Initialize with no token. Token will be fetched via get_token().
        self.token: Optional[str] = None

    def _handle_error(self, message: str, exception: Optional[Exception] = None) -> str:
        """
        Formats and returns a JSON error message string.
        Optionally includes the exception detail.
        """
        return json.dumps({
            "status": "failed",
            "message": f"{message}"
        })

    def _safe_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        json_data: dict = None,
        timeout: int = 10,
        parse_json: bool = True
    ) -> Union[dict, str]:
        """
        Makes an HTTP request with proper error handling and returns the response.
        Returns a parsed JSON dictionary or error JSON string.
        """
        try:
            response = requests.request(method, url, headers=headers, json=json_data, timeout=timeout)
            response.raise_for_status()
            return response.json() if parse_json else response.text

        except requests.exceptions.Timeout:
            return self._handle_error("Connection timed out. The server may be down or slow.")
        except requests.exceptions.ConnectionError as e:
            return self._handle_error("Connection error: Failed to communicate with the payment gateway.", e)
        except requests.exceptions.HTTPError as e:
            return self._handle_error("HTTP error occurred: Failed to communicate with the payment gateway.", e)
        except requests.exceptions.RequestException as e:
            return self._handle_error("Request Error: Failed to communicate with the payment gateway.", e)
        except Exception as e:
            return self._handle_error("Unexpected error: Failed to communicate with the payment gateway.", e)

    def get_token(self) -> Optional[str]:
        """
        Authenticates using credentials and retrieves a bearer token.
        Returns the token if successful, or an error JSON string if failed.
        """
        x_hash = generate_hash(config.USERNAME, config.HASH_KEY)
        headers = {"x-hash": x_hash}
        body = {"userName": config.USERNAME, "password": config.PASSWORD}

        result = self._safe_request("POST", config.TOKEN_URL, headers=headers, json_data=body)
        if isinstance(result, dict) and "token" in result:
            self.token = result["token"]
            return self.token

        return result  # Return error response as JSON string

    def init_payment(self, payload: dict, products: List[ProductItem]) -> str:
        """
        Initializes a payment request with given payload and product list.
        Returns the API response as a JSON string (success or error).
        """
        if not self.token:
            self.get_token()

        tx_id = payload.get("merchantTransactionId")
        x_hash = generate_hash(tx_id, config.HASH_KEY)

        headers = {
            "x-hash": x_hash,
            "Authorization": f"Bearer {self.token}",
        }

        body = {
            **payload,
            "merchantId": config.MERCHANT_ID,
            "storeId": config.STORE_ID,
            "ProductList": [product.dict() for product in products],
        }

        result = self._safe_request("POST", config.INIT_PAYMENT_URL, headers=headers, json_data=body)
        if isinstance(result, str):  # If result is error string
            return result

        if error_msg := result.get("ErrorMessage"):
            return self._handle_error(error_msg)

        return json.dumps({"status": "success", **result})

    def get_transaction_log(self, merchant_transaction_id: str) -> str:
        """
        Retrieves the full transaction log using the provided merchant transaction ID.
        Returns a JSON string of the transaction data or an error.
        """
        if not self.token:
            self.get_token()

        x_hash = generate_hash(merchant_transaction_id, config.HASH_KEY)
        headers = {
            "x-hash": x_hash,
            "Authorization": f"Bearer {self.token}",
        }

        url = f"{config.VERIFY_URL}?merchantTransactionId={merchant_transaction_id}"
        result = self._safe_request("GET", url, headers=headers)

        if isinstance(result, str):  # If result is error string
            return result

        if not result.get("MerchantTransactionId"):
            return json.dumps({"status": "error",  "message": "Invalid Transaction ID"})

        # Convert status to lowercase and return transaction log
        status = result.pop("Status", "").lower()
        return json.dumps({"status": status, **result})

    def get_transaction_status(self, merchant_transaction_id: str) -> str:
        """
        Extracts and formats the key details (status, amount, etc.) from the transaction log.
        Returns a concise status JSON string.
        """
        try:
            raw_data = self.get_transaction_log(merchant_transaction_id)
            data = json.loads(raw_data)

            if data.get("status") == "error":
                return raw_data

            status = data.get("status", "unknown")
            gateway_trx_id = data.get("EPSTransactionId", "Unknown")
            paid_amount = data.get("TotalAmount", "0.00")
            received_amount = data.get("StoreAmount", "0.00")
            payment_method = data.get("FinancialEntity", "Unknown")

            response_data = {
                "status": status,
                "MerchantTransactionId": merchant_transaction_id,
                "EPSTransactionId": gateway_trx_id,
                "paid_amount": paid_amount if status == "success" else "0.00",
                "received_amount": received_amount if status == "success" else "0.00",
                "payment_method": payment_method
            }

            return json.dumps(response_data)

        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
