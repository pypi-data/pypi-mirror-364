import base64
import hashlib
import hmac
import json

from appodus_utils import Utils
from httpx import AsyncClient


class AppodusClientUtils:

    def __init__(self, client_id: str, client_secret: str, api_version: str, http_client: AsyncClient):
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_version = api_version
        self._http_client = http_client

    @property
    def get_api_version(self):
        return self._api_version

    @property
    def get_http_client(self):
        return self._http_client

    def auth_headers(self, method: str, path: str, body: dict = None) -> dict:
        timestamp = str(Utils.datetime_now().timestamp())
        signature = self.generate_signature(
            method=method,
            path=path,
            body=body or {},
            client_secret=self._client_secret,
            timestamp=timestamp,
        )
        return {
            "X-Client-ID": self._client_id,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }

    @staticmethod
    def generate_signature(method: str, path: str, body: dict, client_secret: str, timestamp: str) -> str:
        body_json = json.dumps(body)
        body_hash = hashlib.sha256(body_json.encode()).hexdigest()

        canonical_string = f"{method.upper()}\n{path}\n{timestamp}\n{body_hash}"

        signature = hmac.new(
            key=client_secret.encode(),
            msg=canonical_string.encode(),
            digestmod=hashlib.sha256
        ).digest()

        return base64.b64encode(signature).decode()
