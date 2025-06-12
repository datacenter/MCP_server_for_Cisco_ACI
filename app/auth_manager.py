import httpx
import asyncio
import os
import time
import json
from   dotenv import load_dotenv
import logging

# load .env file for credentials and IP address
load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("APICmcp")

class ApicAuthManager: 
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApicAuthManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def initialize(self):
        if self._initialized:
            logger.info("ApicAuthManager already initialized.")
            return

        async with self._lock:
            if self._initialized:
                return

            logger.info("ApicAuthManager initializing...")
            self.apic_base_url = os.getenv("APIC_BASE_URL")
            self.token_endpoint = f"{self.apic_base_url}/api/aaaLogin.json"
            
            self.username = os.getenv("APIC_USERNAME")
            self.password = os.getenv("APIC_PASSWORD")
            
            self._access_token = None 
            self._token_expiry_time = 0 

            if not self.username or not self.password:
                logger.error("WARNING: APIC_USERNAME or APIC_PASSWORD not set. Authentication will fail.")
            
            # In production, please configure proper SSL certs and verification.
            self._client = httpx.AsyncClient(verify=False) 
            self._initialized = True
            logger.info(f"APICAuthManager initialized. Login Endpoint: {self.token_endpoint}")

    async def get_access_token(self) -> str:
        await self.initialize()
        print("Checking APIC session token...")
        # Check if the token is still valid. APIC token expiry is in 'sessionTimeoutSeconds'.
        # We add a buffer (e.g., 60 seconds) to re-authenticate before it truly expires.
        if self._access_token and self._token_expiry_time > time.time() + 60:
            logger.info("Using existing APIC session token (still valid).")
            return self._access_token 

        print("APIC token expired or not present. Attempting to login...")
        try:
            login_payload = {
                "aaaUser": {
                    "attributes": {
                        "name": self.username,
                        "pwd": self.password
                    }
                }
            }
            
            response = await self._client.post(
                self.token_endpoint,
                json=login_payload,
                timeout=15.0 
            )
            response.raise_for_status()
            data = response.json()
            
            token = data.get("imdata", [{}])[0].get("aaaLogin", {}).get("attributes", {}).get("token")
            session_timeout = int(data.get("imdata", [{}])[0].get("aaaLogin", {}).get("attributes", {}).get("sessionTimeoutSeconds", 600)) # 600s -> 10m

            if not token:
                raise ValueError("APIC session token not found in login response.")

            self._access_token = token
            self._token_expiry_time = time.time() + session_timeout
            
            logger.info(f"Successfully obtained new APIC session token. Expires in {session_timeout} seconds.")
            # httpx manage the 'APIC-Cookie' header from the 'Set-Cookie' response when reusing the client instance
            return self._access_token

        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            try:
                error_details = json.dumps(e.response.json(), indent=2) 
            except json.JSONDecodeError:
                pass
            logger.error(f"APIC Authentication Error (HTTP Status {e.response.status_code}): {error_details}")
            raise RuntimeError(f"APIC authentication failed: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"Network Error during APIC authentication: {e}")
            raise RuntimeError(f"APIC authentication failed due to network error: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during APIC authentication: {e}")
            raise RuntimeError(f"APIC authentication failed: {e}") from e

    async def get_authenticated_client(self) -> httpx.AsyncClient:
        """
        Returns an httpx.AsyncClient instance with the APIC session cookie managed.
        """
        await self.initialize()
        await self.get_access_token() 
        # client automatically includes 'APIC-Cookie' managed by httpx
        return self._client

apic_auth_manager = ApicAuthManager() 
