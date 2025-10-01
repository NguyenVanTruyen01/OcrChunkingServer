import httpx
from typing import Dict, Any, Optional

async def send_webhook(url: str, data: Dict[str, Any], auth: Optional[str] = None):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = auth
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=data, headers=headers)