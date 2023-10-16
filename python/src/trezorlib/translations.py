import json
import struct
from hashlib import sha256
from typing import Any, Dict, List, TextIO, Tuple

import requests

DELIMITER = b"\x00"
MAGIC = b"TRTR"

TranslationData = Dict[str, Dict[str, str]]
HeaderData = Dict[str, str]


def blob_from_file(file: TextIO) -> bytes:
    data = json.load(file)
    return blob_from_dict(data)


def blob_from_url(url: str) -> bytes:
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return blob_from_dict(data)


def blob_from_dict(data: Dict[str, Any]) -> bytes:
    header: HeaderData = data["header"]
    translations: TranslationData = data["translations"]
    return _blob_from_data(header, translations)


def _blob_from_data(header: HeaderData, translations: TranslationData) -> bytes:
    data_blob, items_num = _create_data_blob(translations)

    header_blob = _create_header_blob(
        magic=MAGIC,
        lang=header["language"],
        version=header["version"],
        data_length=len(data_blob),
        items_num=items_num,
        data_hash=sha256(data_blob).digest(),
    )
    assert len(header_blob) == 256

    return header_blob + data_blob


def _create_data_blob(translations: TranslationData) -> Tuple[bytes, int]:
    items_to_write: List[Tuple[str, str]] = []
    for section_name, section in translations.items():
        for k, v in section.items():
            if DELIMITER.decode() in v:
                raise ValueError(f"Delimiter '{DELIMITER}' found in {k}")
            name = f"{section_name}__{k}"
            items_to_write.append((name, v))

    # Sorting alphabetically according the key
    # TODO: maintain a stable order in future versions - write new entries
    # to the end
    items_to_write.sort(key=lambda x: x[0])

    data_blob = b""
    for _key, value in items_to_write:
        data_blob += value.encode()
        data_blob += DELIMITER

    # TODO: try to apply some compression of the data_blob
    return data_blob, len(items_to_write)


def _create_header_blob(
    magic: bytes,
    lang: str,
    version: str,
    data_length: int,
    items_num: int,
    data_hash: bytes,
) -> bytes:
    header = b""

    # Magic (4 bytes)
    header += struct.pack("4s", magic)

    # Version (16 bytes)
    header += struct.pack("16s", version.encode())

    # Language name (32 bytes)
    header += struct.pack("32s", lang.encode())

    # Data length (2 bytes)
    header += struct.pack("H", data_length)

    # Items amount (2 bytes)
    header += struct.pack("H", items_num)

    # Data hash (32 bytes)
    header += struct.pack("32s", data_hash)

    # Fill rest with zeros
    while not len(header) == 256:
        header += struct.pack("B", 0)

    return header
