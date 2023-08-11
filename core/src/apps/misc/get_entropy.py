from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trezor.messages import Entropy, GetEntropy


async def get_entropy(msg: GetEntropy) -> Entropy:
    import trezortranslate as TR
    from trezor.crypto import random
    from trezor.enums import ButtonRequestType
    from trezor.messages import Entropy
    from trezor.ui.layouts import confirm_action

    await confirm_action(
        "get_entropy",
        TR.tr("entropy__title_confirm"),
        TR.tr("entropy__send"),
        TR.tr("words__know_what_your_doing"),
        br_code=ButtonRequestType.ProtectCall,
    )

    size = min(msg.size, 1024)
    entropy = random.bytes(size, True)

    return Entropy(entropy=entropy)
