from micropython import const

from trezor import config

DATA_MAXLENGTH = const(32 * 1024)


def validate_and_set(language_data: bytes, offset: int) -> None:
    from trezor import wire

    if offset + len(language_data) > DATA_MAXLENGTH:
        raise wire.DataError("Language data too long")

    config.translations_set(language_data, offset)


def wipe() -> None:
    config.translations_wipe()
