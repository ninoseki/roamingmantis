import httpx

from . import BaseAdapter


class Instagram(BaseAdapter):
    def _base_url(self):
        return "https://www.instagram.com"

    def url(self):
        # https://www.instagram.com/{}/?__a=1
        return f"{self._base_url()}/{self.id}/?__a=1"

    async def _get(self):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                self.url(),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
                },
            )
            return r.json()

    async def _payload(self):
        json = await self._get()
        return json.get("graphql", {}).get("user", {}).get("biography")
