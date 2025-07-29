import json
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from model_mcp_sdk.exceptions.SdkException import SdkException


class HttpClient:
    def __init__(self, base_url, timeout, max_retries):
        self.base_url = base_url
        self.timeout = timeout / 1000.0  # Convert ms to seconds
        self.session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=max_retries,
            connect=max_retries,
            backoff_factor=0.3,
            status_forcelist=[],
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "PATCH"]),
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send_get(self, endpoint, headers=None):
        return self._execute_request("GET", endpoint, headers=headers)

    def send_post(self, endpoint, headers=None, body=None):
        return self._execute_request("POST", endpoint, headers=headers, body=body)

    def build_endpoint(self, endpoint, path_vars=None, params=None):
        url = endpoint

        # Handle path variables
        if path_vars:
            for var in path_vars:
                url += f"/{urllib.parse.quote(str(var))}"

        # Handle query parameters
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    safe_key = urllib.parse.quote(str(key))
                    safe_value = urllib.parse.quote(str(value))
                    query_params.append(f"{safe_key}={safe_value}")

            if query_params:
                url += "?" + "&".join(query_params)

        return url

    def _execute_request(self, method, endpoint, headers=None, body=None):
        url = self.base_url + endpoint
        print(url)
        headers = headers or {}

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = self.session.post(
                    url, headers=headers, data=body, timeout=self.timeout
                )
            else:
                raise SdkException(1, f"Unsupported method: {method}")

            # Check for unsuccessful responses
            if not response.ok:
                raise SdkException(
                    response.status_code, f"Request failed: {response.reason}"
                )

            return response.text

        except requests.exceptions.RequestException as e:
            code = e.response.status_code if e.response else 1
            message = str(e)
            raise SdkException(code, message)
