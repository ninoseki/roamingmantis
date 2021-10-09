from . import BaseAdapter


class Pinterest(BaseAdapter):
    def _base_url(self):
        return "https://www.pinterest.com"

    async def _payload(self):
        html = await self._get()
        metas = html.find("meta")
        abouts = [
            meta for meta in metas if meta.attrs.get("property") == "pinterestapp:about"
        ]
        if len(abouts) == 0:
            return

        about = abouts[0]
        content = about.attrs.get("content")
        if "----" in content:
            return content.split("----")[-1]

        return content

    async def find_c2(self):
        return await self.payload()
