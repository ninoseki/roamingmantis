import base64
import functools
import re
import sys
import zlib
from typing import Any, Dict, List

import aiometer
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes.apk import APK
from loguru import logger

from roamingmantis.moqhao.adapter.blogger import Blogger
from roamingmantis.moqhao.adapter.blogspot import Blogspot
from roamingmantis.moqhao.adapter.google import Google
from roamingmantis.moqhao.adapter.instagram import Instagram
from roamingmantis.moqhao.adapter.pinterest import Pinterest
from roamingmantis.moqhao.adapter.vk import VK
from roamingmantis.moqhao.adapter.youtube import YouTube

BYTES_TO_SKIP = 4
KEY = b"Ab5d1Q32"


def parse_apk(path: str):
    try:
        apk = APK(path)
        return apk
    except Exception:
        return None


def decrypt_dex(data):
    # credit: https://securelist.com/roaming-mantis-part-iv/90332/
    try:
        decompressed = zlib.decompress(data[BYTES_TO_SKIP:])
        b64decoded = base64.b64decode(decompressed)
        vm = dvm.DalvikVMFormat(b64decoded)
        logger.debug("Decrypted as type A")
        return vm
    except Exception:
        logger.debug("Failed to decrypt as type A")
        return None


def decrypt_dex_b(data):
    try:
        first_byte = data[BYTES_TO_SKIP]
        byte_array = []
        for idx in range(BYTES_TO_SKIP + 1, len(data)):
            byte_array.append(data[idx] ^ first_byte)
        decompressed = zlib.decompress(bytes(byte_array))
        b64decoded = base64.b64decode(decompressed)
        vm = dvm.DalvikVMFormat(b64decoded)
        logger.debug("Decrypted as type B")
        return vm
    except Exception:
        logger.debug("Failed to decrypt as type B")
        return None


def find_hidden_dex(apk: APK):
    files = apk.get_files()
    hidden_dex_names = [x for x in files if re.match(r"assets/[a-z0-9]+/[a-z0-9]+", x)]
    if len(hidden_dex_names) == 1:
        hidden_dex_name = hidden_dex_names[0]
        data = apk.get_file(hidden_dex_name)
        dex = decrypt_dex(data)
        if dex is not None:
            return dex
        return decrypt_dex_b(data)

    return None


def build_adapter(id: str, provider: str):
    if provider == "youtube":
        return YouTube(id)
    elif provider == "ins":
        return Instagram(id)
    elif provider == "GoogleDoc":
        return Google(id)
    elif provider == "GoogleDoc2":
        return Google(id)
    elif provider == "blogger":
        return Blogger(id)
    elif provider == "vk":
        return VK(id)
    elif provider == "blogspot":
        return Blogspot(id)
    elif provider == "pinterest":
        return Pinterest(id)
    else:
        return


def list_to_dict(items):
    memo = {}
    for item in items:
        for key in item.keys():
            memo[key] = item[key]
    return memo


async def find_c2(strings: List[str]):
    accounts = [x for x in strings if re.match(r"^[a-z0-9]+\|.+", x)]
    if len(accounts) != 1:
        return []

    adapters = []
    for account in accounts[0].split("|")[1:]:
        logger.debug(f"1st C2 = {account}")

        id_, provider = account.split("@")
        adapter = build_adapter(id_, provider)
        if adapter is None:
            continue
        adapters.append(adapter)

    async def run_adapter(adapter):
        _c2 = await adapter.find_c2()
        if _c2 is None:
            return {
                adapter.url(): {
                    "payload": await adapter.payload(),
                    "error": "failed to analyze it",
                }
            }
        else:
            return {
                adapter.url(): {"payload": await adapter.payload(), "destination": _c2}
            }

    jobs = [functools.partial(run_adapter, adapter) for adapter in adapters]
    results = await aiometer.run_all(jobs, max_at_once=10)
    return list_to_dict(results)


async def find_phishing(strings: List[str]):
    accounts = [
        x for x in strings if re.match(r"https:\/\/www\.pinterest\.com/[a-z0-9]+\/", x)
    ]

    adapters = []
    for account in accounts:
        id_ = account.split("/")[-2]
        adapter = build_adapter(id_, "pinterest")
        if adapter is None:
            continue
        adapters.append(adapter)

    async def run_adapter(adapter):
        return {adapter.url(): await adapter.find_c2()}

    jobs = [functools.partial(run_adapter, adapter) for adapter in adapters]
    results = await aiometer.run_all(jobs, max_at_once=10)
    return list_to_dict(results)


async def analyze(path: str, extract_dex: bool = True) -> Dict[str, Any]:
    apk = parse_apk(path)
    if apk is None:
        logger.error("Invalid apk is given")
        sys.exit(1)

    dex = find_hidden_dex(apk)
    if dex is None:
        logger.error("Failed to parse dex")
        sys.exit(1)

    output = {}

    if extract_dex:
        filename = f"{path}.dex"
        with open(filename, "wb") as fp:
            fp.write(dex.get_buff())
            output["dex"] = f"hidden dex is extracted as {filename}"

    strings = [string for string in dex.get_strings()]
    output["c2"] = await find_c2(strings)
    output["phishing"] = await find_phishing(strings)
    return output
