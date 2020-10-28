from . import BaseAdapter


class VK(BaseAdapter):
    def _base_url(self):
        return "https://vk.com"

    def url(self):
        # "https://m.vk.com/%s?act=info
        return f"https://m.vk.com/{self.id}?act=info"

    async def _payload(self):
        html = await self._get()
        print(html.text)
        selector = "#mcont > div > div > div.profile_info > div > div > dl > dd > a"
        profile = html.find(selector, first=True)
        if profile is None:
            return
        else:
            return profile.text
