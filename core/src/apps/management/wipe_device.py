from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trezor.messages import Success, WipeDevice


async def wipe_device(msg: WipeDevice) -> Success:
    import storage
    import trezortranslate as TR
    from trezor.enums import ButtonRequestType
    from trezor.messages import Success
    from trezor.ui.layouts import confirm_action

    from apps.base import reload_settings_from_storage

    await confirm_action(
        "confirm_wipe",
        TR.tr("wipe__title"),
        TR.tr("wipe__info"),
        TR.tr("wipe__want_to_wipe"),
        reverse=True,
        verb=TR.tr("buttons__hold_to_confirm"),
        hold=True,
        hold_danger=True,
        br_code=ButtonRequestType.WipeDevice,
    )

    storage.wipe()
    reload_settings_from_storage()

    return Success(message="Device wiped")
