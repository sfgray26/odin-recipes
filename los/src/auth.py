import httpx
import logging
from .config import TOKEN_URL, CLIENT_ID, CLIENT_SECRET, PROXY, VERIFY_SSL

logger = logging.getLogger(__name__)

access_token = None

async def get_access_token():
    global access_token
    if access_token:
        return access_token
    
    async with httpx.AsyncClient(proxies=PROXY, verify=VERIFY_SSL) as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("Access token obtained successfully")
        return access_token