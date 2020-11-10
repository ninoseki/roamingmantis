import base64
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from Crypto.Cipher import DES
from httpx import HTTPError
from requests_html import HTML


class BaseAdapter(ABC):
    def __init__(self, id: str):
        self.id = id
        self.bytes_to_skip = 4
        self.key = b"Ab5d1Q32"

    @abstractmethod
    def _base_url(self) -> str:
        raise NotImplementedError()

    def url(self) -> str:
        return f"{self._base_url()}/{self.id}"

    async def _get(self) -> HTML:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url())
            return HTML(html=r.text)

    @abstractmethod
    async def _payload(self) -> str:
        raise NotImplementedError()

    async def payload(self) -> Optional[str]:
        try:
            return await self._payload()
        except HTTPError:
            pass

        return None

    def _bytes_to_skip(self) -> int:
        return 4

    async def decrypt(self) -> Optional[bytes]:
        payload = await self.payload()
        if payload is None:
            return None

        b = base64.urlsafe_b64decode(payload)
        des = DES.new(self.key, 2, self.key)
        decrypted = des.decrypt(b)
        return decrypted[: -self.bytes_to_skip]

    async def find_c2(self) -> Optional[str]:
        try:
            decrypted = await self.decrypt()
            if decrypted is None:
                return None

            return "".join([chr for chr in decrypted.decode() if ord(chr) >= 32])
        except ValueError:
            pass

        return None
