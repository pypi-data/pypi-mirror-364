# eps_gateway/utils.py

import base64
import hashlib
import hmac

def generate_hash(data: str, secret_key: str) -> str:
    encoded_key = secret_key.encode("utf-8")
    encoded_data = data.encode("utf-8")
    hmac_digest = hmac.new(encoded_key, encoded_data, hashlib.sha512).digest()
    return base64.b64encode(hmac_digest).decode()
