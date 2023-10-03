from micropython import const

from storage.device import LANGUAGE_MAXLENGTH
from trezor import config

# We want to store the language name together with the data
# (at the beginning). Accounting also for the delimiter (+1).
DATA_MAXLENGTH = const(32 * 1024)
TRANSLATIONS_MAXLENGTH = DATA_MAXLENGTH - (LANGUAGE_MAXLENGTH + 1)


def write(data: bytes, offset: int) -> None:
    from trezor import wire

    if offset + len(data) > DATA_MAXLENGTH:
        raise wire.DataError("Language data too long")

    config.translations_set(data, offset)


def wipe() -> None:
    config.translations_wipe()
