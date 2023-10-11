from micropython import const
from typing import TYPE_CHECKING

from trezor.wire import DataError

if TYPE_CHECKING:
    from trezor.messages import ChangeLanguage, Success

_CHUNK_SIZE = const(1024)
_HEADER_SIZE = const(256)
_FILL_BYTE = b"\x00"


class TranslationsHeader:
    MAGIC = b"TRTR"
    LANG_LEN = 32
    VERSION_LEN = 16
    DATA_HASH_LEN = 32

    def __init__(
        self,
        language: str,
        version: str,
        data_length: int,
        items_num: int,
        data_hash: bytes,
    ):
        self.language = language
        self.version = version
        self.data_length = data_length
        self.items_num = items_num
        self.data_hash = data_hash

    @classmethod
    def from_bytes(cls, data: bytes) -> "TranslationsHeader":
        from trezor.utils import BufferReader

        from apps.common import readers

        if len(data) != _HEADER_SIZE:
            raise DataError("Invalid header length")

        try:
            r = BufferReader(data)

            magic = r.read(len(cls.MAGIC))
            if magic != cls.MAGIC:
                raise DataError("Invalid header magic")

            version = r.read(cls.VERSION_LEN).rstrip(_FILL_BYTE).decode()
            language = r.read(cls.LANG_LEN).rstrip(_FILL_BYTE).decode()
            data_length = readers.read_uint16_le(r)
            items_num = readers.read_uint16_le(r)
            data_hash = r.read(cls.DATA_HASH_LEN)

            # Rest must be empty bytes
            for b in r.read():
                if b != 0:
                    raise DataError("Invalid header data")

            return cls(
                language=language,
                version=version,
                data_length=data_length,
                items_num=items_num,
                data_hash=data_hash,
            )
        except EOFError:
            raise DataError("Invalid header data")


async def change_language(msg: ChangeLanguage) -> Success:
    from trezor import translations
    from trezor.messages import Success

    data_length = msg.data_length  # local_cache_attribute

    # When empty data, reverting the language to default (english)
    if data_length == 0:
        await _require_confirm_change_language("")
        translations.wipe()
        return Success(message="Language reverted to default")

    if data_length > translations.DATA_MAXLENGTH:
        raise DataError("Translations too long")
    if data_length < _HEADER_SIZE:
        raise DataError("Translations too short")

    data_left = data_length
    offset = 0

    # Getting and parsing the header
    header_data = await get_data_chunk(_HEADER_SIZE, offset)
    header = TranslationsHeader.from_bytes(header_data)

    if header.data_length + _HEADER_SIZE != data_length:
        raise DataError("Invalid header data length")

    # TODO: verify the hash of the data (get all of them and hash them)
    # TODO: verify the header signature (signature of sha256(header))

    # Confirm with user and wipe old data
    await _require_confirm_change_language(header.language)
    translations.wipe()

    # Write the header
    translations.write(header_data, offset)
    offset += len(header_data)
    data_left -= len(header_data)

    # Requesting the data in chunks and saving them
    while data_left > 0:
        data_chunk = await get_data_chunk(data_left, offset)
        translations.write(data_chunk, offset)
        data_left -= len(data_chunk)
        offset += len(data_chunk)

    return Success(message="Language changed")


async def get_data_chunk(data_left: int, offset: int) -> bytes:
    from trezor.messages import TranslationDataAck, TranslationDataRequest
    from trezor.wire.context import call

    data_length = min(data_left, _CHUNK_SIZE)
    req = TranslationDataRequest(data_length=data_length, data_offset=offset)
    res = await call(req, TranslationDataAck)
    return res.data_chunk


async def _require_confirm_change_language(language: str) -> None:
    from trezor.enums import ButtonRequestType
    from trezor.ui.layouts import confirm_action
    from trezortranslate import TR

    # TODO: might also show the length of the data, so user can check it with client?
    # Empty language means default language (english)
    if language:
        description = TR.language__change_template.format(language)
    else:
        description = TR.language__set_default
    await confirm_action(
        "set_language",
        TR.language__title_change,
        description=description,
        br_code=ButtonRequestType.ProtectCall,
    )
