import requests
import hashlib
import uuid
import cloudinary.uploader
from .exceptions import CashItAPIError
from .models import ChequeMetadata, ChequeStatusResponse, ChequeIssueRequest, ChequeVerifyRequest

class CashItClient:
    def __init__(self, api_key, base_url, cloudinary_config):
        self.api_key = api_key
        self.base_url = base_url
        cloudinary.config(**cloudinary_config)

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def deposit_cheque(self, file_path, metadata: ChequeMetadata):
        upload_result = cloudinary.uploader.upload(file_path)
        image_url = upload_result["secure_url"]

        payload = {
            "image_url": image_url,
            "account_number": metadata.account_number,
            "bank_code": metadata.bank_code,
            "amount": metadata.amount,
            "payer_name": metadata.payer_name,
        }
        response = requests.post(f"{self.base_url}/cheque/deposit/init", json=payload, headers=self._headers())
        if response.status_code != 200:
            raise CashItAPIError(response.text)
        return response.json()

    def get_cheque_status(self, ref_id):
        response = requests.get(f"{self.base_url}/cheque/status/{ref_id}", headers=self._headers())
        if response.status_code != 200:
            raise CashItAPIError(response.text)
        return ChequeStatusResponse(**response.json())

    def issue_digital_cheque(self, req: ChequeIssueRequest):
        payload = req.dict()
        raw_data = f"{req.account_number}|{req.bank_code}|{req.amount}|{req.expiry_date}"
        payload["signature"] = hashlib.sha256(raw_data.encode()).hexdigest()

        response = requests.post(f"{self.base_url}/cheque/issue", json=payload, headers=self._headers())
        if response.status_code != 200:
            raise CashItAPIError(response.text)
        return response.json()

    def verify_cheque(self, req: ChequeVerifyRequest):
        response = requests.post(f"{self.base_url}/cheque/verify", json=req.dict(), headers=self._headers())
        if response.status_code != 200:
            raise CashItAPIError(response.text)
        return response.json()
