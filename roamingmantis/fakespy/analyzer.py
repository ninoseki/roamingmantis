import base64
import re
from io import BytesIO
from typing import Dict, List, Optional
from zipfile import ZipFile

from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from Crypto.Cipher import AES, DES
from loguru import logger

KEY = base64.decodebytes(b"MkXOl0e30PeWG01t7cTKjA==")
URL_WHITE_LIST = [
    "https://twitter.com/siumakuaw",
    "http://kuronekoamato.com/",
    "http://jppost.picp.io/",
    "http://liankt.club/",
    "https://twitter.com/sekadeta",
]


def get_des_key(key: str) -> bytes:
    array = bytearray(8)
    bytes_ = key.encode()
    for i in range(len(bytes_)):
        array[i] = bytes_[i]

    return bytes(array)


def hex2byte(string: str) -> bytes:
    bytes_ = string.encode()
    array = bytearray(int(len(bytes_) / 2))

    for i in range(0, len(bytes_), 2):
        char = bytes_[i : i + 2].decode()
        idx = int(i / 2)
        array[idx] = int(char, 16)

    return bytes(array)


def decrypt_c2(encrypted_key: str, key: str = "TEST") -> str:
    des = DES.new(get_des_key(key))
    bytes_ = hex2byte(encrypted_key)
    decrypted: bytes = des.decrypt(bytes_)
    decrypted_string: str = decrypted.decode()
    return "".join([chr for chr in decrypted_string if ord(chr) >= 32])


def extract_zip(input_zip) -> Dict[str, bytes]:
    input_zip = ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}


def parse_apk(path: str) -> Optional[APK]:
    try:
        apk = APK(path)
        return apk
    except Exception as e:
        logger.exception(e)
        logger.error("Failed to parse as an apk!")
        return None


def decrypt_dex(data: bytes) -> Optional[DalvikVMFormat]:
    try:
        aes = AES.new(KEY)
        decrypted = aes.decrypt(data)
        zipfile = BytesIO(decrypted)
        zip_dict = extract_zip(zipfile)
        dex = zip_dict.get("classes.dex")
        if dex is None:
            return None
        return DalvikVMFormat(dex)
    except Exception as e:
        logger.exception(e)
        logger.error("Failed to decrypt!")
        return None


def find_hidden_dex(apk: APK) -> Optional[DalvikVMFormat]:
    files = apk.get_files()
    hidden_dex_names = [x for x in files if re.match(r"assets/[a-zA-Z0-9]+", x)]
    if len(hidden_dex_names) == 1:
        hidden_dex_name = hidden_dex_names[0]
        data = apk.get_file(hidden_dex_name)
        return decrypt_dex(data)

    return None


def find_urls(strings: List[str]) -> List[str]:
    decrpyted_keys: List[str] = []
    for encrypted_key in strings:
        if not encrypted_key.isalnum():
            continue

        try:
            decrpyted_keys.append(decrypt_c2(encrypted_key))
        except Exception:
            continue

    return [x for x in decrpyted_keys if x.startswith(("https://", "http://"))]


def find_c2(urls: List[str]) -> List[str]:
    return list(set(urls) - set(URL_WHITE_LIST))


def analyze(
    path: str, extract_dex: bool = False, verbose: bool = False
) -> Optional[dict]:
    apk = parse_apk(path)
    if apk is None:
        return None

    dex = find_hidden_dex(apk)
    if dex is None:
        return None

    if extract_dex:
        filename = f"{path}.dex"
        with open(filename, "wb") as fp:
            fp.write(dex.get_buff())
            logger.info(f"A hidden dex is extracted as {filename}")

    strings = [string for string in dex.get_strings()]
    urls = find_urls(strings)
    c2 = find_c2(urls)

    output = {}
    output["c2"] = c2
    if verbose:
        output["hardcoded_urls"] = urls

    return output
