from micropython import const

from trezor import config

DATA_MAXLENGTH = const(32 * 1024)
DEFAULT_LANGUAGE = "en-US"


def get_language() -> str:
    from trezortranslate import language_name

    translation_lang = language_name()
    if translation_lang:
        return translation_lang
    return DEFAULT_LANGUAGE


def write(data: bytes, offset: int) -> None:
    from trezor import wire

    if offset + len(data) > DATA_MAXLENGTH:
        raise wire.DataError("Language data too long")

    config.translations_set(data, offset)


def wipe() -> None:
    config.translations_wipe()
