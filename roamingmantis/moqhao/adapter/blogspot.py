from . import BaseAdapter


class Blogspot(BaseAdapter):
    def _base_url(self):
        return ""

    def url(self):
        # https://{}.blogspot.com/?m=1
        return f"https://{self.id}.blogspot.com/?m=1"

    async def _payload(self):
        html = await self._get()
        selector = "#Profile1 > div > div > div > dl > dt > a"
        profile = html.find(selector, first=True)
        if profile is None:
            return
        else:
            return profile.text
