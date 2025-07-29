import json
import operator
import hmac
import urllib.parse
import hashlib


class WoohooSignatureGeneratorHelper:
    def __init__(self, client_secret):
        self.client_secret = client_secret.encode('utf-8')

    @staticmethod
    def url_encode(data):
        return urllib.parse.quote_plus(data)

    @staticmethod
    def sort_data(data):
        return dict(sorted(data.items(), key=operator.itemgetter(0)))

    def sort_payload(self, payload):
        for key, value in payload.items():
            if isinstance(value, list):
                if len(value) > 1:
                    payload[key] = [self.sort_data(item) for item in value]
                else:
                    payload[key] = [self.sort_data(value[0])]
            elif isinstance(value, dict):
                payload[key] = self.sort_data(value)
        return self.sort_data(payload)

    @staticmethod
    def sort_query_parameters(url):
        query_parts = url.split('?')
        if len(query_parts) > 1:
            base_url, query_string = query_parts
            query_pairs = query_string.split('&')
            sorted_query = "&".join(sorted(query_pairs))
            return f"{base_url}?{sorted_query}"
        return url

    def generate_signature(self, request_body, abs_api_url, request_http_method):
        http_method = request_http_method.upper()
        sorted_url = self.sort_query_parameters(abs_api_url)
        encoded_url = self.url_encode(sorted_url)
        concatenated_string = f"{http_method}&{encoded_url}"

        if request_body:
            sorted_payload = self.sort_payload(request_body)
            payload_json = json.dumps(sorted_payload, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            encoded_payload = urllib.parse.quote(payload_bytes, safe='')
            concatenated_string += f"&{encoded_payload}"

        signature_bytes = concatenated_string.encode('utf-8')
        signature = hmac.new(self.client_secret, signature_bytes, hashlib.sha512).hexdigest()
        return signature
