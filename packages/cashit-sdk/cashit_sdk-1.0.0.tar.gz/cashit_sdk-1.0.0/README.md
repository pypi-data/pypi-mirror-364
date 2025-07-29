# CashIt Python SDK

Production-ready Python SDK for CashIt digital cheque APIs.

## Features
- Deposit cheque (via Cloudinary)
- Lookup cheque status
- Issue digital cheques (SHA256-signed)
- Verify authenticity and expiry

## Install

```bash
pip install requests cloudinary
```

## Usage

```python
from cashit_sdk.client import CashItClient, ChequeMetadata, ChequeIssueRequest

cloudinary_config = {
    "cloud_name": "YOUR_NAME",
    "api_key": "YOUR_KEY",
    "api_secret": "YOUR_SECRET"
}

client = CashItClient(api_key="your_api_key", base_url="https://api.cashit.ng", cloudinary_config=cloudinary_config)

metadata = ChequeMetadata(account_number="1234567890", bank_code="058", amount=50000, payer_name="John Doe")
result = client.deposit_cheque("/path/to/cheque.jpg", metadata)
print(result)
```
