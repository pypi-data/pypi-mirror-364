from dataclasses import dataclass

@dataclass
class ChequeMetadata:
    account_number: str
    bank_code: str
    amount: float
    payer_name: str

@dataclass
class ChequeStatusResponse:
    status: str
    created_at: str
    image_url: str

@dataclass
class ChequeIssueRequest:
    account_number: str
    bank_code: str
    amount: float
    expiry_date: str

@dataclass
class ChequeVerifyRequest:
    account_number: str
    bank_code: str
    amount: float
    expiry_date: str
    signature: str
