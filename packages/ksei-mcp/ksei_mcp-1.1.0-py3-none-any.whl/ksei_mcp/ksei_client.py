"""KSEI API Client - Python"""

import json
import time
import hashlib
import base64
from enum import Enum
from typing import List, Dict, Any, Optional, Protocol
from dataclasses import dataclass
from urllib.parse import quote
import requests
import jwt
from fake_useragent import UserAgent


class PortfolioType(Enum):
    EQUITY = "EKUITAS"
    MUTUAL_FUND = "REKSADANA"
    CASH = "KAS"
    BOND = "OBLIGASI"
    OTHER = "LAINNYA"
    
    def name(self) -> str:
        return {
            self.EQUITY: "equity",
            self.MUTUAL_FUND: "mutual_fund", 
            self.CASH: "cash",
            self.BOND: "bond",
            self.OTHER: "other"
        }.get(self, "unknown")


@dataclass
class PortfolioSummaryDetails:
    type: str
    amount: float
    percent: float
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            type=data["type"],
            amount=data["summaryAmount"],
            percent=data["percent"]
        )


@dataclass 
class PortfolioSummaryResponse:
    total: float
    details: List[PortfolioSummaryDetails]
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            total=data["summaryValue"],
            details=[PortfolioSummaryDetails.from_dict(d) for d in data["summaryResponse"]]
        )


@dataclass
class CashBalance:
    id: int
    account_number: str
    bank_id: str
    currency: str
    balance: float
    balance_idr: float
    status: int
    
    def current_balance(self) -> float:
        return max(self.balance, self.balance_idr)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            account_number=data["rekening"],
            bank_id=data["bank"],
            currency=data["currCode"],
            balance=data["saldo"],
            balance_idr=data["saldoIdr"],
            status=data["status"]
        )


@dataclass
class CashBalanceResponse:
    data: List[CashBalance]
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data=[CashBalance.from_dict(d) for d in data["data"]])


@dataclass
class ShareBalance:
    account: str
    full_name: str
    participant: str
    balance_type: str
    currency: str
    amount: float
    closing_price: float
    
    def valid(self) -> bool:
        return bool(self.account and self.full_name)
    
    def current_value(self) -> float:
        return self.amount * self.closing_price
    
    def symbol(self) -> str:
        return self.full_name.split(" - ")[0]
    
    def name(self) -> str:
        parts = self.full_name.split(" - ")
        return parts[1] if len(parts) > 1 else ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            account=data["rekening"],
            full_name=data["efek"],
            participant=data["partisipan"],
            balance_type=data["tipeSaldo"],
            currency=data["curr"],
            amount=data["jumlah"],
            closing_price=data["harga"]
        )


@dataclass
class ShareBalanceResponse:
    total: float
    data: List[ShareBalance]
    
    def remove_invalid_data(self):
        self.data = [b for b in self.data if b.valid()]
    
    @classmethod
    def from_dict(cls, data: dict):
        response = cls(
            total=data["summaryValue"],
            data=[ShareBalance.from_dict(d) for d in data["data"]]
        )
        response.remove_invalid_data()
        return response


@dataclass
class LoginRequest:
    id: str
    app_type: str
    username: str
    password: str


@dataclass
class LoginResponse:
    validation: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(validation=data["validation"])


@dataclass
class GlobalIdentity:
    login_id: str
    username: str
    email: str
    phone: str
    full_name: str
    investor_id: str
    investor_name: str
    citizen_id: str
    passport_id: str
    tax_id: str
    card_id: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            login_id=data["idLogin"],
            username=data["username"],
            email=data["email"],
            phone=data["phone"],
            full_name=data["fullName"],
            investor_id=data["investorId"],
            investor_name=data["sidName"],
            citizen_id=data["nikId"],
            passport_id=data["passportId"],
            tax_id=data["npwp"],
            card_id=data["cardId"]
        )


@dataclass
class GlobalIdentityResponse:
    code: str
    status: str
    identities: List[GlobalIdentity]
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            code=data["Code"],
            status=data["Status"],
            identities=[GlobalIdentity.from_dict(d) for d in data["Identities"]]
        )


class AuthStore(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str) -> None: ...


class FileAuthStore:
    def __init__(self, directory: str):
        import os
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
    
    def _get_path(self, key: str) -> str:
        import os
        return os.path.join(self.directory, f"{key}.json")
    
    def get(self, key: str) -> Optional[str]:
        try:
            with open(self._get_path(key), 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def set(self, key: str, value: str) -> None:
        with open(self._get_path(key), 'w') as f:
            json.dump(value, f)


def get_expire_time(token: str) -> Optional[float]:
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("exp")
    except jwt.InvalidTokenError:
        return None


class Client:
    def __init__(self, auth_store: Optional[AuthStore] = None, username: str = "", 
                 password: str = "", plain_password: bool = True):
        self.base_url = "https://akses.ksei.co.id/service"
        self.base_referer = "https://akses.ksei.co.id"
        self.auth_store = auth_store
        self.username = username
        self.password = password
        self.plain_password = plain_password
        self.ua = UserAgent()
    
    def _hash_password(self) -> str:
        if not self.plain_password:
            return self.password
        
        password_sha1 = hashlib.sha1(self.password.encode()).hexdigest()
        timestamp = int(time.time())
        param = f"{password_sha1}@@!!@@{timestamp}"
        encoded_param = base64.b64encode(param.encode()).decode()
        
        url = f"{self.base_url}/activation/generated?param={quote(encoded_param)}"
        
        response = requests.get(url, headers={
            "Referer": self.base_referer,
            "User-Agent": self.ua.random
        })
        response.raise_for_status()
        
        data = response.json()
        if not data.get("data"):
            raise ValueError(f"No data in activation response: {data}")
        
        return data["data"][0]["pass"]
    
    def _login(self) -> str:
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
        
        hashed_password = self._hash_password()
        
        login_data = {
            "username": self.username,
            "password": hashed_password,
            "id": "1",
            "appType": "web"
        }
        
        response = requests.post(
            f"{self.base_url}/login?lang=id",
            json=login_data,
            headers={
                "Referer": self.base_referer,
                "User-Agent": self.ua.random,
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        login_response = LoginResponse.from_dict(response.json())
        token = login_response.validation
        
        if self.auth_store:
            self.auth_store.set(self.username, token)
        
        return token
    
    def _get_token(self) -> str:
        if not self.auth_store:
            return self._login()
        
        token = self.auth_store.get(self.username)
        if not token:
            return self._login()
        
        expire_time = get_expire_time(token)
        if not expire_time or expire_time < time.time():
            return self._login()
        
        return token
    
    def get(self, path: str) -> dict:
        token = self._get_token()
        
        response = requests.get(
            f"{self.base_url}{path}",
            headers={
                "Referer": self.base_referer,
                "User-Agent": self.ua.random,
                "Authorization": f"Bearer {token}"
            }
        )
        response.raise_for_status()
        return response.json()
    
    def set_auth(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def set_base_url(self, base_url: str):
        self.base_url = base_url
    
    def set_plain_password(self, plain_password: bool):
        self.plain_password = plain_password
    
    def get_portfolio_summary(self) -> PortfolioSummaryResponse:
        data = self.get("/myportofolio/summary")
        return PortfolioSummaryResponse.from_dict(data)
    
    def get_cash_balances(self) -> CashBalanceResponse:
        data = self.get(f"/myportofolio/summary-detail/{PortfolioType.CASH.value.lower()}")
        return CashBalanceResponse.from_dict(data)
    
    def get_share_balances(self, portfolio_type: PortfolioType) -> ShareBalanceResponse:
        if portfolio_type == PortfolioType.CASH:
            raise ValueError("get_share_balances does not accept cash type")
        
        data = self.get(f"/myportofolio/summary-detail/{portfolio_type.value.lower()}")
        return ShareBalanceResponse.from_dict(data)
    
    def get_global_identity(self) -> GlobalIdentityResponse:
        data = self.get("/myaccount/global-identity/")
        return GlobalIdentityResponse.from_dict(data)
    

def example():
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    if not username or not password:
        raise ValueError("EMAIL and PASSWORD must be set in .env file")
    
    auth_store = FileAuthStore(directory="auth_store")
    
    client = Client(auth_store=auth_store, username=username, password=password)
    
    try:
        summary = client.get_portfolio_summary()
        print("Portfolio Summary:", summary)
        
        cash_balances = client.get_cash_balances()
        print("Cash Balances:", cash_balances)
        
        share_balances = client.get_share_balances(PortfolioType.EQUITY)
        print("Share Balances:", share_balances)

        # export to .json        
        with open("portfolio_summary.json", "w") as f:
            json.dump(summary, f, default=lambda o: o.__dict__, indent=4)
        with open("cash_balances.json", "w") as f:
            json.dump(cash_balances, f, default=lambda o: o.__dict__, indent=4)
        with open("share_balances.json", "w") as f:
            json.dump(share_balances, f, default=lambda o: o.__dict__, indent=4)
        
    except Exception as e:
        print(f"An error occurred: {e}")