from __future__ import annotations

import json

from validate_same_keys import DIR

file = DIR / "cs.json"

data = json.loads(file.read_text())["translations"]

DELIMITER = "*"

items_to_write: list[tuple[str, str]] = []
lengths: list[tuple[str, int]] = []
highest_v_len = 0
for section_name, section in data.items():
    num = 0
    length = 0
    for k, v in section.items():
        if DELIMITER in v:
            raise ValueError(f"Delimiter '{DELIMITER}' found in {k}")
        name = f"{section_name}__{k}"
        items_to_write.append((name, v))
        num += 1
        v_len = len(v.encode())
        if v_len > highest_v_len:
            highest_v_len = v_len
        length += v_len
    print(f"{section_name}: {num}, {length}")
    lengths.append((section_name, length))
items_to_write.sort(key=lambda x: x[0])
lengths.sort(key=lambda x: x[1])
print(lengths)
print("highest_v_len", highest_v_len)

altcoins = ["cardano", "eos", "nem", "tezos", "stellar"]

buffer_str = ""
for index, (key, value) in enumerate(items_to_write):
    # if any(key.startswith(f"{altcoin}__") for altcoin in altcoins):
    #     continue
    value_newlines_encoded = value.replace("\n", "\\n").replace("\r", "\\r")
    # buffer_str += f"{key}:::{value_newlines_encoded}---"
    # buffer_str += f"{index}:::{value_newlines_encoded}---"
    buffer_str += f"{value_newlines_encoded}{DELIMITER}"
print("buffer_str", buffer_str)
print("buffer_str", buffer_str.encode())
print("buffer_str", len(buffer_str))
print("buffer_str", len(buffer_str.encode()))
