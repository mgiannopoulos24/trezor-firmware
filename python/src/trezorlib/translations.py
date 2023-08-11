import json
from typing import Dict, List, TextIO, Tuple

import requests

DELIMITER = "*"


def blob_from_file(file: TextIO) -> bytes:
    data: Dict[str, Dict[str, str]] = json.load(file)
    return _blob_from_data(data)


def blob_from_url(url: str) -> bytes:
    r = requests.get(url)
    r.raise_for_status()
    data: Dict[str, Dict[str, str]] = r.json()
    return _blob_from_data(data)


def _blob_from_data(data: Dict[str, Dict[str, str]]) -> bytes:
    items_to_write: List[Tuple[str, str]] = []
    for section_name, section in data.items():
        for k, v in section.items():
            if DELIMITER in v:
                raise ValueError(f"Delimiter '{DELIMITER}' found in {k}")
            name = f"{section_name}__{k}"
            items_to_write.append((name, v))
    # Sorting alphabetically according the key
    items_to_write.sort(key=lambda x: x[0])

    buffer_str = ""
    for _key, value in items_to_write:
        value_newlines_encoded = value.replace("\n", "\\n").replace("\r", "\\r")
        buffer_str += f"{value_newlines_encoded}{DELIMITER}"

    return buffer_str.encode()
