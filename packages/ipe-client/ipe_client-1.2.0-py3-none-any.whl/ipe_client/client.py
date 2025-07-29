import httpx
import json

class IPEClient:
    """
    An asynchronous client for the IPE API.
    
    This client handles authentication and provides methods for interacting
    with the IPE image processing services.
    """
    def __init__(self, base_url: str, username: str, password: str, client_timeout: float = 30.0):
        if not all([base_url, username, password]):
            raise ValueError("base_url, username, and password must be provided.")
            
        self.base_url = base_url.rstrip('/') # Ensure no trailing slash
        self.username = username
        self.password = password
        self.access_token = None
        
        self._client = httpx.AsyncClient(timeout=client_timeout)

    async def _ensure_authenticated(self):
        if not self.access_token:
            await self._authenticate()

    async def _authenticate(self):
        auth_url = f"{self.base_url}/auth/token"
        payload = {'username': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = await self._client.post(auth_url, headers=headers, data=payload)
            response.raise_for_status()
            
            response_json = response.json()
            self.access_token = response_json.get("access_token")
            if not self.access_token:
                raise ConnectionError("Authentication succeeded but 'access_token' was missing in response.")

        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error during authentication: {e.response.status_code} - {e.response.text}"
            raise ConnectionError(f"IPE Authentication failed: {error_message}") from e
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error during authentication: {e}") from e
        except json.JSONDecodeError:
            raise ConnectionError("Failed to decode JSON response from authentication endpoint.")

    async def _get_headers(self, content_type="application/json"):
        await self._ensure_authenticated()
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": content_type}

    async def submit_batch_job_to_ipe(self, image_urls: list[str], system_prompt: str, user_prompt: str, model_name: str, preprocessing_options: dict) -> list:
        await self._ensure_authenticated()
        endpoint = f"{self.base_url}/image-to-text/v1/process-batch-image-urls"
        payload = {"urls": [str(url) for url in image_urls], "system_prompt": system_prompt, "user_prompt": user_prompt, "model_name": model_name, "preprocessing_options": preprocessing_options}
        headers = await self._get_headers()
        response = await self._client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    async def check_ipe_job_status(self, job_ids: list[str]) -> dict:
        await self._ensure_authenticated()
        endpoint = f"{self.base_url}/image-to-text/v1/status/job-ids"
        payload = {"job_ids": job_ids}
        headers = await self._get_headers()
        response = await self._client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()