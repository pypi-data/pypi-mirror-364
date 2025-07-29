import base64
import datetime
import httpx
import uuid
from django.utils import timezone as django_timezone
from django.contrib.contenttypes.models import ContentType

from .models import PlatformToken, PlatformPaymentRequestLog
from django_woohoo.signature import WoohooSignatureGeneratorHelper
from django_woohoo.utils import get_env_variable
from django_woohoo.dataclasses import PaymentInitiateTransactionDataClass


BASE_URL = get_env_variable("WOOHOO_BASE_URL")


class AmazonCouponClient:
    def __init__(self, user):
        self.client_id = get_env_variable("WOOHOO_CLIENT_ID")
        self.client_secret = get_env_variable("WOOHOO_CLIENT_SECRET")
        self.username = get_env_variable("WOOHOO_USERNAME")
        self.password = get_env_variable("WOOHOO_PASSWORD")        

        self.user = user
        self.bearer_token = self._get_bearer_token()

    def _get_bearer_token(self):
        try:
            token_obj = PlatformToken.objects.get(name=PlatformToken.NameChoices.AMAZON_BEARER)
            age = django_timezone.now() - token_obj.modified
            if age.days > 6:
                raise PlatformToken.DoesNotExist
            return self._decode_string(token_obj.token)
        except PlatformToken.DoesNotExist:
            return self._generate_bearer_token()

    def _generate_bearer_token(self):
        auth_code = self._get_authorization_token()

        url = f"{BASE_URL}/oauth2/token"
        payload = {
            "authorizationCode": auth_code,
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }

        headers = {"Content-Type": "application/json"}
        response = httpx.post(url, json=payload, headers=headers)
        self._create_log(url, payload, response.status_code, response.text)

        if response.status_code != 200:
            raise httpx.HTTPStatusError("Failed to get bearer token", request=response.request, response=response)

        access_token = response.json().get("token")
        if not access_token:
            raise ValueError("Access token not found in response.")

        PlatformToken.objects.update_or_create(
            name=PlatformToken.NameChoices.AMAZON_BEARER,
            defaults={"token": self._encode_string(access_token)}
        )

        return access_token

    def _get_authorization_token(self):
        try:
            token_obj = PlatformToken.objects.get(name=PlatformToken.NameChoices.AMAZON_AUTHORIZATION)
            age = django_timezone.now() - token_obj.modified
            if age.days > 6:
                raise PlatformToken.DoesNotExist
            return self._decode_string(token_obj.token)
        except PlatformToken.DoesNotExist:
            return self._generate_authorization_token()

    def _generate_authorization_token(self):
        url = f"{BASE_URL}/oauth2/verify"
        payload = {
            "clientId": self.client_id,
            "username": self.username,
            "password": self.password
        }

        headers = {"Content-Type": "application/json"}
        response = httpx.post(url, json=payload, headers=headers)
        self._create_log(url, payload, response.status_code, response.text)

        if response.status_code != 200:
            raise httpx.HTTPStatusError("Failed to verify user", request=response.request, response=response)

        authorization_code = response.json().get("authorizationCode")
        if not authorization_code:
            raise ValueError("Authorization code not found in response.")

        PlatformToken.objects.update_or_create(
            name=PlatformToken.NameChoices.AMAZON_AUTHORIZATION,
            defaults={"token": self._encode_string(authorization_code)}
        )

        return authorization_code

    def _create_log(self, url, data, response_status, response_text):
        PlatformPaymentRequestLog.objects.create(
            payment_provider=PlatformPaymentRequestLog.PaymentProviderChoices.AMAZON,
            url=url,
            body=data,
            response=response_text,
            response_status=response_status,
            requested_user_content_type=ContentType.objects.get_for_model(self.user),
            requested_user_object_id=self.user.id,      
            requested_user_frozen_details={}  
        )

    def _encode_string(self, s: str) -> str:
        return base64.b64encode(s.encode("utf-8")).decode("utf-8")

    def _decode_string(self, s: str) -> str:
        return base64.b64decode(s.encode("utf-8")).decode("utf-8")

    def _process_request(self, url, method, data=None, params=None):
        signature_gen = WoohooSignatureGeneratorHelper(self.client_secret)
        signature = signature_gen.generate_signature(data or {}, url, method)

        headers = {
            'Content-Type': 'application/json',
            'dateAtClient': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'signature': signature,
            'Authorization': f"Bearer {self.bearer_token}"
        }

        if method == 'post':
            response = httpx.post(url, json=data, headers=headers)
        elif method == 'get':
            response = httpx.get(url, headers=headers, params=params or {})
        else:
            raise ValueError("Unsupported HTTP method")

        response_text = response.text
        if response.status_code == 200:
            response_text = response.json()

        self._create_log(url, data, response.status_code, response_text)
        return response.status_code, response_text

    def process_amount(self, data: PaymentInitiateTransactionDataClass, sku_code):
        per_amount = int(data.transfer_amount)
        quantity = 1
        amount = per_amount * quantity
        ref_no = str(uuid.uuid4()).replace("-", "_")

        request_data = {
            "address": {
                "firstname": data.beneficiary_details.beneficiary_name,
                "email": data.beneficiary_details.beneficiary_email,
                "telephone": data.beneficiary_details.beneficiary_phone,
                "country": "IN",
                "postcode": "560076",
            },
            "billing": {
                "firstname": data.beneficiary_details.beneficiary_name,
                "email": data.beneficiary_details.beneficiary_email,
                "telephone": data.beneficiary_details.beneficiary_phone,
                "country": "IN",
                "postcode": "560076",
            },
            "payments": [
                {
                    "code": "svc",
                    "amount": amount,
                    "poNumber": str(uuid.uuid4()).replace("-", "_"),
                }
            ],
            "refno": ref_no,
            "deliveryMode": "API",
            "products": [
                {
                    "sku": sku_code,
                    "price": per_amount,
                    "qty": quantity,
                    "currency": 356,
                }
            ],
            "syncOnly": True,
        }

        url = f"{BASE_URL}/rest/v3/orders"
        return self._process_request(url, "post", request_data)
