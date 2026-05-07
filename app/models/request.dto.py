import httpx
from config.settings import settings

class HttpClient:
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT
        )
        
    async def get(self, url: str):
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()