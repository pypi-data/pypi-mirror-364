from datetime import date

import aiohttp


class WBClient:
    BASE_URL = "https://common-api.wildberries.ru"

    def __init__(self, api_key: str, session: aiohttp.ClientSession | None = None):
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession(headers={"Authorization": self.api_key})

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_seller_info(self):
        url = f"{self.BASE_URL}/api/v1/seller-info"
        params = {}
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def get_news(self, *, from_dt: date = None, from_id: int = None):
        if from_dt and from_id:
            raise ValueError("Only one of from_dt or from_id can be specified")
        if not from_dt and not from_id:
            raise ValueError("One of from_dt or from_id must be specified")
        if from_id:
            params = {"fromID": from_id}
        else:
            params = {"from": from_dt.isoformat()}
        url = f"{self.BASE_URL}/api/communications/v2/news"
        async with self.session.get(url, params=params) as resp:
            return await resp.json()
