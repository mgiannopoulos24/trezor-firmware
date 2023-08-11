from __future__ import annotations

czech_chars: list[tuple[str, str]] = [
    ("Á", "0xC381"),
    ("Č", "0xC48C"),
    ("Ď", "0xC48E"),
    ("É", "0xC389"),
    ("Ě", "0xC49A"),
    ("Í", "0xC38D"),
    ("Ň", "0xC587"),
    ("Ó", "0xC393"),
    ("Ř", "0xC598"),
    ("Š", "0xC5A0"),
    ("Ť", "0xC5A4"),
    ("Ú", "0xC39A"),
    ("Ů", "0xC5AE"),
    ("Ý", "0xC39D"),
    ("Ž", "0xC5BD"),
    ("á", "0xC3A1"),
    ("č", "0xC48D"),
    ("ď", "0xC48F"),
    ("é", "0xC3A9"),
    ("ě", "0xC49B"),
    ("í", "0xC3AD"),
    ("ň", "0xC588"),
    ("ó", "0xC3B3"),
    ("ř", "0xC599"),
    ("š", "0xC5A1"),
    ("ť", "0xC5A5"),
    ("ú", "0xC3BA"),
    ("ů", "0xC5AF"),
    ("ý", "0xC3BD"),
    ("ž", "0xC5BE"),
]

french_chars: list[tuple[str, str]] = [
    ("À", "0xC380"),
    ("Â", "0xC382"),
    ("Æ", "0xC386"),
    ("Ç", "0xC387"),
    ("È", "0xC388"),
    ("É", "0xC389"),
    ("Ê", "0xC38A"),
    ("Ë", "0xC38B"),
    ("Î", "0xC38E"),
    ("Ï", "0xC38F"),
    ("Ô", "0xC394"),
    ("Ù", "0xC399"),
    ("Û", "0xC39B"),
    ("Ü", "0xC39C"),
    ("Ÿ", "0xC5B8"),
    ("Œ", "0xC592"),
    ("à", "0xC3A0"),
    ("â", "0xC3A2"),
    ("æ", "0xC3A6"),
    ("ç", "0xC3A7"),
    ("è", "0xC3A8"),
    ("é", "0xC3A9"),
    ("ê", "0xC3AA"),
    ("ë", "0xC3AB"),
    ("î", "0xC3AE"),
    ("ï", "0xC3AF"),
    ("ô", "0xC3B4"),
    ("ù", "0xC3B9"),
    ("û", "0xC3BB"),
    ("ü", "0xC3BC"),
    ("ÿ", "0xC3BF"),
    ("œ", "0xC593"),
]

# Need to deduplicate, some chars may be the same in more languages
# (want to keep the order, so not using set operation)
non_english_chars: list[tuple[str, str]] = []
for entry in czech_chars + french_chars:
    if entry not in non_english_chars:
        non_english_chars.append(entry)

if __name__ == "__main__":
    # Generating a C function for getting the index from utf8 value
    template = """\
const uint8_t utf8_mapping(uint16_t c_2bytes) {
  switch (c_2bytes) {
XXXXXXXXXXXXXXXXXXXX
    default: return 0; // non-printable
  }
}
"""
    lines: list[str] = []
    for index, (key, value) in enumerate(non_english_chars):
        line = f"    case {value}: return {127 + index}; // {key}"
        lines.append(line)
    function = template.replace("XXXXXXXXXXXXXXXXXXXX", "\n".join(lines))
    print(function)
