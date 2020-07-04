from . import BaseAdapter


class VK(BaseAdapter):
    def _base_url(self):
        return "https://vk.com"

    async def _payload(self):
        html = await self._get()
        selector = "#profile_full > div > div.profile_info > div > div.labeled"
        profile = html.find(selector, first=True)
        if profile is None:
            return
        else:
            return profile.text
