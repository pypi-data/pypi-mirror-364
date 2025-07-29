import base64
import io
import json
import os
import time
from pathlib import Path

import requests
from PIL import Image


class EndpointClient:
    """
    Client for calling an endpoint.
    """

    def __init__(
        self,
        api_url: str = "https://kkl0vxv34qoe57en.eu-west-1.aws.endpoints.huggingface.cloud",
        token: str | None = None,
        timeout: int = 50,
    ):
        self.api_url = api_url
        self.token = token
        self.timeout = timeout

        if self.token is None:
            self.token = self.get_secret("HF_TOKEN")

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from:

        - Environment variable if available
        - Git-crypt encrypted secrets file if configured

        Args:
            secret_name (str): Name of the secret to retrieve

        Returns:
            str: The secret value

        Raises:
            ValueError: If the secret is not found in any source
        """

        # 1. Check environment variables first (highest priority)
        env_value = os.getenv(secret_name)
        if env_value:
            return env_value

        # 2. Check git-crypt encrypted secrets file
        secrets_file = Path(".secrets.json")
        if secrets_file.exists():
            try:
                with open(secrets_file, "r", encoding="utf-8") as f:
                    secrets = json.load(f)
                    if secret_name in secrets:
                        return secrets[secret_name]
            except (json.JSONDecodeError, IOError) as e:
                raise ValueError(f"Error reading secrets file: {e}") from e

        # 3. Secret not found in any source
        raise ValueError(
            f"Secret '{secret_name}' not found. "
            f"Please set it as an environment variable or add it to .secrets.json file."
        )

    def call_with_image_path(self, image_path: str, image_format: str = "jpeg") -> dict:
        """
        Call the environment segmentation endpoint with an image file path.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": f"image/{image_format}",
        }

        with open(image_path, "rb") as f:
            data = f.read()

        response = requests.post(self.api_url, headers=headers, data=data, timeout=self.timeout)
        return response.json()

    def call_with_pil_image(self, image: Image.Image, threshold: float = 0.5) -> dict:
        """
        Call the environment segmentation endpoint with a PIL Image.
        Sends a JSON payload with base64-encoded image.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        payload = {"inputs": img_base64, "parameters": {"threshold": threshold}}

        response = requests.post(
            self.api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=self.timeout,
        )
        return response.json()

    def wait_until_ready(self, total_timeout: int = 5 * 60, interval: int = 5) -> bool:
        """
        Poll the endpoint until it is ready or timeout is reached.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()

        while time.time() - start_time < total_timeout:
            try:
                response = requests.head(self.api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return True
                elif response.status_code == 503:
                    time.sleep(interval)
                else:
                    print(f"Unexpected status: {response.status_code}")
                    time.sleep(interval)
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                time.sleep(interval)

        print("Timeout reached. Endpoint is not responding.")
        return False
