from . import BaseAdapter


class Blogger(BaseAdapter):
    def _base_url(self):
        return "https://www.blogger.com/profile"

    async def _payload(self):
        html = await self._get()
        title = html.find("#maia-main > div > h1", first=True)
        if title is None:
            return

        return str(title.text)
