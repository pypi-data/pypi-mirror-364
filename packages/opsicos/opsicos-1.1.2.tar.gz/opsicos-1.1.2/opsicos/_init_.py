# The entire package code is now in this one file for simplicity and robustness.
# This is version 1.1.1, the corrected version.
import requests
import json

__version__ = "1.1.2"


class OpsicosClient:
    """
    A professional Python SDK for the Opsicos AI Gateway.
    """

    def __init__(self, api_key: str, base_url: str = "https://opsicos-api.onrender.com"):
        """
        Initializes the client with your credentials.

        Args:
            api_key (str): Your personal Opsicos API key.
            base_url (str, optional): The base URL of the API. Defaults to the Render service URL.
        """
        if not api_key:
            raise ValueError("API key is required to initialize the OpsicosClient.")

        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, payload):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=payload, stream=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request to {url} failed: {e}") from e

    def chat(self, messages, model="gpt-4o"):
        """
        Sends a chat request to the Opsicos API.
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        return self._make_request('POST', 'chat', {"model": model, "messages": messages})

    def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024"):
        """
        Sends an image generation request to the Opsicos API.
        """
        return self._make_request('POST', 'images/generate', {"model": model, "prompt": prompt, "size": size})

    def chat_stream(self, messages, model="gpt-4o"):
        """
        Sends a streaming chat request to the Opsicos API.
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        url = f"{self.base_url}/chat/stream"

        try:
            response = requests.post(url, headers=self.headers, json={"model": model, "messages": messages},
                                     stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith(b'data:'):
                    try:
                        data_str = line.decode('utf-8')[5:].strip()
                        if data_str:
                            yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API stream request to {url} failed: {e}") from e