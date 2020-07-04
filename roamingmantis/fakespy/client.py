from json.decoder import JSONDecodeError
from typing import Dict, Optional, cast

import httpx
from httpx._exceptions import HTTPError
from loguru import logger


class Client:
    def __init__(self, c2: str, mobile_number: str):
        self.base_url = f"http://{c2}"
        self.mobile_number = mobile_number
        self.default_headers = {
            "ser-Agent": "Fiddler",
            "Content-Type": "application/json",
        }
        self.default_payload = {"json": {"mobile": self.mobile_number}}

    def _post(
        self, url: str, payload: Dict, headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        headers = self.default_headers if headers is None else headers

        r = httpx.post(url, headers=headers, json=payload)
        try:
            r.raise_for_status()
            return cast(Dict, r.json())
        except HTTPError:
            logger.error(f"{url} returns {r.status_code}")
        except JSONDecodeError:
            logger.error(f"{url} returns an invalid JSON")
            logger.error(r.text)

        return None

    def get_message(self):
        url = f"{self.base_url}//servlet/GetMessage"
        return self._post(url, self.default_payload)

    def get_message2(self):
        url = f"{self.base_url}//servlet/GetMessage2"
        return self._post(url, self.default_payload)

    def get_more_message(self):
        url = f"{self.base_url}//servlet/GetMoreMessage"
        return self._post(url, self.default_payload)

    def get_more_con_message(self):
        url = f"{self.base_url}//servlet/GetMoreConMessage"
        return self._post(url, self.default_payload)

    def move_url(self):
        payload = {"json": {"res": "kk"}}
        url = f"{self.base_url}//servlet/MoveURL"
        return self._post(url, payload)

    def query(self, command: str):
        if command == "GetMessage":
            return self.get_message()

        if command == "GetMessage2":
            return self.get_message2()

        if command == "GetMoreMessage":
            return self.get_more_message()

        if command == "GetMoreConMessage":
            return self.get_more_con_message()

        if command == "MoveURL":
            return self.move_url()

        raise Exception(f"{command} is not supported.")
