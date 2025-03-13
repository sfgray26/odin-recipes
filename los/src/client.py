import asyncio
import httpx
import logging
from .auth import get_access_token
from .config import PROXY, VERIFY_SSL, BASE_DELAY, MAX_RETRIES

logger = logging.getLogger(__name__)

async def make_request_with_retry(url, headers, method="GET", data=None):
    retries = 0

    while retries < MAX_RETRIES:
        try:
            async with httpx.AsyncClient(proxies=PROXY, verify=VERIFY_SSL) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        wait_time = BASE_DELAY * (2 ** retries) + (0.1 * retries)
                    logger.warning(f"Rate limit reached. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                elif response.status_code == 401 and retries == 0:
                    logger.warning("Token expired. Refreshing token and retrying...")
                    headers["Authorization"] = f"Bearer {await get_access_token()}"
                else:
                    response.raise_for_status()
                    return response

        except httpx.RequestError as e:
            logger.warning(f"Request failed: {e}. Retrying...")
            wait_time = BASE_DELAY * (2 ** retries) + (0.1 * retries)
            await asyncio.sleep(wait_time)

        retries += 1

    logger.error("Max retries reached. Failing request.")
    raise httpx.HTTPStatusError("Max retries reached", request=None, response=None)