from . import BaseAdapter


class Google(BaseAdapter):
    def __init__(self, id: str):
        super().__init__(id)
        self.bytes_to_skip = 5

    def _base_url(self):
        return "https://docs.google.com/document/d"

    def url(self):
        # https://docs.google.com/document/d/{}/mobilebasic
        return f"{self._base_url()}/{self.id}/mobilebasic"

    async def _payload(self):
        html = await self._get()
        title = html.find("title", first=True).text
        return title.split("/")[0]

    async def find_c2(self):
        id = await self._payload()
        self.id = id
        return await super().find_c2()
