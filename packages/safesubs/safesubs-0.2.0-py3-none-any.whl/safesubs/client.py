import aiohttp
import asyncio
from cachetools import TTLCache

class SafeSubsClient:
    def __init__(self, api_token: str, api_url: str = "https://subs.sxve.it/v1/check", ttl_minutes: int = 24*60, max_size: int = 100_000):
        self.api_token = api_token
        self.api_url = api_url
        # TTLCache: maxsize + ttl (в секундах)
        self._cache = TTLCache(maxsize=max_size, ttl=ttl_minutes * 60)

    async def __call__(self, user_id: int) -> bool:
        # если в кеше уже True — возвращаем
        if self._cache.get(user_id):
            return True

        # иначе идём на сервер
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={"user_id": user_id, "auth_token": self.api_token}
            ) as resp:
                if resp.status != 200:
                    return False

                data = await resp.json()
                result = data.get("status", False)

                if result:
                    # читаем TTL от сервера или берём дефолт
                    ttl_minutes = data.get("cache_ttl", 24*60)
                    # обновляем TTLCache с новым TTL для этого ключа
                    self._cache.ttl = ttl_minutes * 60
                    self._cache[user_id] = True

                return result
