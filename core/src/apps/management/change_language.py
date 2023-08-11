from micropython import const
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trezor.messages import ChangeLanguage, Success, TranslationDataAck

_CHUNK_SIZE = const(1024)


async def change_language(msg: ChangeLanguage) -> Success:
    import storage.device as storage_device
    import storage.translations as storage_translations
    from trezor import wire
    from trezor.messages import Success

    language = msg.language  # local_cache_attribute
    data_length = msg.data_length  # local_cache_attribute

    if len(language) > storage_device.LANGUAGE_MAXLENGTH:
        raise wire.DataError("Language identifier too long")

    if data_length > storage_translations.DATA_MAXLENGTH:
        raise wire.DataError("Translations too long")

    # When empty data, reverting the language to default (english)
    if data_length == 0:
        language = ""

    await _require_confirm_change_language(language)
    storage_translations.wipe()

    # Requesting the data in chunks and saving them
    if data_length > 0:
        offset = 0
        data_left = data_length
        while data_left > 0:
            resp = await send_request_chunk(data_left)
            data_left -= len(resp.data_chunk)
            storage_translations.validate_and_set(resp.data_chunk, offset)
            offset += len(resp.data_chunk)

    storage_device.set_language(language)

    return Success(message="Language changed")


async def send_request_chunk(data_left: int) -> TranslationDataAck:
    from trezor.messages import TranslationDataAck, TranslationDataRequest
    from trezor.wire.context import call

    req = TranslationDataRequest()
    req.data_length = min(data_left, _CHUNK_SIZE)
    return await call(req, TranslationDataAck)


async def _require_confirm_change_language(language: str) -> None:
    import trezortranslate as TR
    from trezor.enums import ButtonRequestType
    from trezor.ui.layouts import confirm_action

    # TODO: might also show the length of the data, so user can check it with client?
    # Empty language means default language (english)
    if language:
        description = TR.tr("language__change_template").format(language)
    else:
        description = TR.tr("language__set_default")
    await confirm_action(
        "set_language",
        TR.tr("language__title_change"),
        description=description,
        br_code=ButtonRequestType.ProtectCall,
    )
