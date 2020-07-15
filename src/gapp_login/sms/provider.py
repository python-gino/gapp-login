import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Optional

import httpx


class SMSError(Exception):
    def __init__(self, error: Optional[str] = None) -> None:
        self.error = error

    def __repr__(self) -> str:
        return f"SMSError(error={self.error!r})"


class SMSBaseProvider:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def send_login_code(self, phone_num: str, code: str, ttl: int = 300):
        raise NotImplementedError


class Tencent(SMSBaseProvider):
    def __init__(self,
                 secret_id: str,
                 secret_key: str,
                 sms_app_id: str,
                 sms_template_id: str,
                 sms_sign: str):
        super().__init__()
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.service = "sms"
        self.sms_app_id = sms_app_id
        self.sms_template_id = sms_template_id
        self.sms_sign = sms_sign
        self.host = "sms.tencentcloudapi.com"
        self.endpoint = f"https://{self.host}"

    def sign(self, params: dict, timestamp: int, http_method: str = "POST"):
        """Tencent API sign method

        Refs https://cloud.tencent.com/document/api/382/38767
        """

        algorithm = "TC3-HMAC-SHA256"
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # format request string
        uri = "/"
        querystring = ""
        ct = "application/json; charset=utf-8"
        payload = json.dumps(params)
        headers = f"content-type:{ct}\nhost:{self.host}\n"
        signed_headers = "content-type;host"
        hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        request = (f"{http_method}\n{uri}\n{querystring}\n{headers}\n"
                   f"{signed_headers}\n{hashed_payload}")

        # format sign string
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_request = hashlib.sha256(request.encode("utf-8")).hexdigest()
        string_to_sign = (f"{algorithm}\n{str(timestamp)}\n"
                          f"{credential_scope}\n{hashed_request}")

        # sign request
        def _sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        secret_date = _sign(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = _sign(secret_date, self.service)
        secret_signing = _sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"),
                             hashlib.sha256).hexdigest()

        # put together to get an Authorization string
        return (f"{algorithm} Credential={self.secret_id}/{credential_scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}")

    async def send_sms(self,
                       phone_nums: list,
                       sms_sign: str,
                       template_id: str,
                       template_params: list):
        params = {
            "SmsSdkAppid": self.sms_app_id,
            "TemplateID": template_id,
            "Sign": sms_sign,
            "PhoneNumberSet": phone_nums,
            "TemplateParamSet": template_params,
        }
        timestamp = int(time.time())
        authorization = self.sign(params, timestamp)
        resp = await self.client.post(
            self.endpoint,
            json=params,
            headers={
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": self.host,
                "X-TC-Action": "SendSms",
                "X-TC-Timestamp": str(timestamp),
                "X-TC-Version": "2019-07-11",
            },
        )

        return resp

    async def send_login_code(self, phone_num: str, code: str, ttl: int):
        resp = await self.send_sms(
            [phone_num],
            self.sms_sign,
            self.sms_template_id,
            [code, str(int(ttl/60))])

        resp = resp.json()

        status = resp.get("Response", {}).get("SendStatusSet", [])
        status = status[0] if status else None
        if not status or status.get("Code") != "Ok":
            raise SMSError(error=f"SMS Error: {status.get('Message')}")

        return status
