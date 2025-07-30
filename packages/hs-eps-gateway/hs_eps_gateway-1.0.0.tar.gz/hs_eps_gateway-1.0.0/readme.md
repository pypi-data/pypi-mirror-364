
# Easy Payment Gateway (EPS) Client (`hs_eps_gateway`)

A lightweight and reusable Python client for interacting with the [Easy Payment Gateway (EPS)](https://eps.com.bd), designed to work in Django, Flask, FastApi and any standard Python environment.

---

## 🚀 Features

- Authenticate and retrieve access tokens from EPS
- Initialize new payments with product details
- Check full transaction logs
- Retrieve clean transaction status with parsed data
- Built-in error handling and JSON responses

---

## 📦 Installation

```bash
pip install hs-eps-gateway
```

## Configuration (Environment Variables)

| Variable | Description |
|--|--|
| EPS_USERNAME | Your EPS account email |
| EPS_PASSWORD | Your EPS password |
| EPS_HASH_KEY | Provided hash key from EPS |
| EPS_MERCHANT_ID | Your merchant ID |
| EPS_STORE_ID | Your store ID |
| EPS_TOKEN_URL | (Optional) Auth URL (default provided) |
| EPS_INIT_PAYMENT_URL | (Optional) Payment init URL |
| EPS_VERIFY_URL | (Optional) Transaction verify URL |

## 🧠 Usage

1. Initialize Payment
	```python 
    from hs_eps_gateway.client import EPSClient
	from hs_eps_gateway.esp_types import ProductItem

	client = EPSClient()

	payload = {
	    "CustomerOrderId": "ORDER1234544121a",
	    "merchantTransactionId": "TXN2025072300144121a",
	    "transactionTypeId": 1,
	    "totalAmount": 10,
	    "successUrl": "https://yoursite.com/success",
	    "failUrl": "https://yoursite.com/fail",
	    "cancelUrl": "https://yoursite.com/cancel",
	    "customerName": "Test User",
	    "customerEmail": "test@example.com",
	    "CustomerAddress": "Dhaka",
	    "CustomerCity": "Dhaka",
	    "CustomerState": "Dhaka",
	    "CustomerPostcode": "1230",
	    "CustomerCountry": "BD",
	    "CustomerPhone": "019XXXXXXXX",
	    "ProductName": "Test Product",
	}

	products = [
	    ProductItem(
	        ProductName="Product1",
	        NoOfItem="1",
	        ProductProfile="general",
	        ProductCategory="test",
	        ProductPrice="10"
	    )
	]

	response = client.init_payment(payload, products)
	print(response)
	```


2. Get Transaction Log
	```python 
	from hs_eps_gateway.client import EPSClient

	client = EPSClient()
	
	log = client.get_transaction_log("TXN2025072300144121a")
	print(log)
	```

3. Get Transaction Status (Short Summary)
	```python 
		from hs_eps_gateway.client import EPSClient

		client = EPSClient()
		status = client.get_transaction_status("TXN2025072300144121a")
		print(status)
	```
## 📄 License

MIT License.

## 🙋‍♂️ Author
Name: Himel
 [Portfolio](https://himelrana.com). Contributions are welcome!