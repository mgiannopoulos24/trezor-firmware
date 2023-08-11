from typing import TYPE_CHECKING

import trezortranslate as TR
from trezor.enums import ButtonRequestType
from trezor.ui.layouts import confirm_properties

from ..helpers import eos_asset_to_string, eos_name_to_string

if TYPE_CHECKING:
    from typing import Iterable

    from trezor.messages import (
        EosActionBuyRam,
        EosActionBuyRamBytes,
        EosActionCommon,
        EosActionDelegate,
        EosActionDeleteAuth,
        EosActionLinkAuth,
        EosActionNewAccount,
        EosActionRefund,
        EosActionSellRam,
        EosActionTransfer,
        EosActionUndelegate,
        EosActionUnlinkAuth,
        EosActionUpdateAuth,
        EosActionVoteProducer,
        EosAuthorization,
    )
    from trezor.ui.layouts import PropertyType


# Whether action is last - and should be HoldToConfirm
is_last = False


# Because icon and br_code are almost always the same
# (and also calling with positional arguments takes less space)
async def _confirm_properties(
    br_type: str,
    title: str,
    props: Iterable[PropertyType],
) -> None:
    await confirm_properties(
        br_type,
        title,
        props,
        hold=is_last,
        br_code=ButtonRequestType.ConfirmOutput,
    )


async def confirm_action_buyram(msg: EosActionBuyRam) -> None:
    await _confirm_properties(
        "confirm_buyram",
        TR.tr("eos__buy_ram"),
        (
            (TR.tr("eos__payer"), eos_name_to_string(msg.payer)),
            (TR.tr("eos__receiver"), eos_name_to_string(msg.receiver)),
            (TR.tr("eos__amount"), eos_asset_to_string(msg.quantity)),
        ),
    )


async def confirm_action_buyrambytes(msg: EosActionBuyRamBytes) -> None:
    await _confirm_properties(
        "confirm_buyrambytes",
        TR.tr("eos__buy_ram"),
        (
            (TR.tr("eos__payer"), eos_name_to_string(msg.payer)),
            (TR.tr("eos__receiver"), eos_name_to_string(msg.receiver)),
            (TR.tr("eos__bytes"), str(msg.bytes)),
        ),
    )


async def confirm_action_delegate(msg: EosActionDelegate) -> None:
    props = [
        (TR.tr("eos__sender"), eos_name_to_string(msg.sender)),
        (TR.tr("eos__receiver"), eos_name_to_string(msg.receiver)),
        (TR.tr("eos__cpu"), eos_asset_to_string(msg.cpu_quantity)),
        (TR.tr("eos__net"), eos_asset_to_string(msg.net_quantity)),
    ]
    append = props.append  # local_cache_attribute
    if msg.transfer:
        append((TR.tr("eos__transfer"), TR.tr("eos__yes")))
        append((TR.tr("eos__receiver"), eos_name_to_string(msg.receiver)))
    else:
        append((TR.tr("eos__transfer"), TR.tr("eos__no")))

    await _confirm_properties(
        "confirm_delegate",
        TR.tr("eos__delegate"),
        props,
    )


async def confirm_action_sellram(msg: EosActionSellRam) -> None:
    await _confirm_properties(
        "confirm_sellram",
        TR.tr("eos__sell_ram"),
        (
            (TR.tr("eos__receiver"), eos_name_to_string(msg.account)),
            (TR.tr("eos__bytes"), str(msg.bytes)),
        ),
    )


async def confirm_action_undelegate(msg: EosActionUndelegate) -> None:
    await _confirm_properties(
        "confirm_undelegate",
        TR.tr("eos__undelegate"),
        (
            (TR.tr("eos__sender"), eos_name_to_string(msg.sender)),
            (TR.tr("eos__receiver"), eos_name_to_string(msg.receiver)),
            (TR.tr("eos__cpu"), eos_asset_to_string(msg.cpu_quantity)),
            (TR.tr("eos__net"), eos_asset_to_string(msg.net_quantity)),
        ),
    )


async def confirm_action_refund(msg: EosActionRefund) -> None:
    await _confirm_properties(
        "confirm_refund",
        TR.tr("eos__refund"),
        ((TR.tr("eos__owner"), eos_name_to_string(msg.owner)),),
    )


async def confirm_action_voteproducer(msg: EosActionVoteProducer) -> None:
    producers = msg.producers  # local_cache_attribute

    if msg.proxy and not producers:
        # PROXY
        await _confirm_properties(
            "confirm_voteproducer",
            TR.tr("eos__vote_for_proxy"),
            (
                (TR.tr("eos__voter"), eos_name_to_string(msg.voter)),
                (TR.tr("eos__proxy"), eos_name_to_string(msg.proxy)),
            ),
        )

    elif producers:
        # PRODUCERS
        await _confirm_properties(
            "confirm_voteproducer",
            TR.tr("eos__vote_for_producers"),
            (
                (f"{wi:2d}. {eos_name_to_string(producer)}", None)
                for wi, producer in enumerate(producers, 1)
            ),
        )

    else:
        # Cancel vote
        await _confirm_properties(
            "confirm_voteproducer",
            TR.tr("eos__cancel_vote"),
            ((TR.tr("eos__voter"), eos_name_to_string(msg.voter)),),
        )


async def confirm_action_transfer(msg: EosActionTransfer, account: str) -> None:
    props = [
        (TR.tr("eos__from"), eos_name_to_string(msg.sender)),
        (TR.tr("eos__to"), eos_name_to_string(msg.receiver)),
        (TR.tr("eos__amount"), eos_asset_to_string(msg.quantity)),
        (TR.tr("eos__contract"), account),
    ]
    if msg.memo is not None:
        props.append((TR.tr("eos__memo"), msg.memo[:512]))
    await _confirm_properties(
        "confirm_transfer",
        TR.tr("eos__transfer").replace(":", ""),
        props,
    )


async def confirm_action_updateauth(msg: EosActionUpdateAuth) -> None:
    props: list[PropertyType] = [
        (TR.tr("eos__account"), eos_name_to_string(msg.account)),
        (TR.tr("eos__permission"), eos_name_to_string(msg.permission)),
        (TR.tr("eos__parent"), eos_name_to_string(msg.parent)),
    ]
    props.extend(authorization_fields(msg.auth))
    await _confirm_properties(
        "confirm_updateauth",
        TR.tr("eos__update_auth"),
        props,
    )


async def confirm_action_deleteauth(msg: EosActionDeleteAuth) -> None:
    await _confirm_properties(
        "confirm_deleteauth",
        TR.tr("eos__delete_auth"),
        (
            (TR.tr("eos__account"), eos_name_to_string(msg.account)),
            (TR.tr("eos__permission"), eos_name_to_string(msg.permission)),
        ),
    )


async def confirm_action_linkauth(msg: EosActionLinkAuth) -> None:
    await _confirm_properties(
        "confirm_linkauth",
        TR.tr("eos__link_auth"),
        (
            (TR.tr("eos__account"), eos_name_to_string(msg.account)),
            (TR.tr("eos__code"), eos_name_to_string(msg.code)),
            (TR.tr("eos__type"), eos_name_to_string(msg.type)),
            (TR.tr("eos__requirement"), eos_name_to_string(msg.requirement)),
        ),
    )


async def confirm_action_unlinkauth(msg: EosActionUnlinkAuth) -> None:
    await _confirm_properties(
        "confirm_unlinkauth",
        TR.tr("eos__unlink_auth"),
        (
            (TR.tr("eos__account"), eos_name_to_string(msg.account)),
            (TR.tr("eos__code"), eos_name_to_string(msg.code)),
            (TR.tr("eos__type"), eos_name_to_string(msg.type)),
        ),
    )


async def confirm_action_newaccount(msg: EosActionNewAccount) -> None:
    props: list[PropertyType] = [
        (TR.tr("eos__creator"), eos_name_to_string(msg.creator)),
        (TR.tr("eos__name"), eos_name_to_string(msg.name)),
    ]
    props.extend(authorization_fields(msg.owner))
    props.extend(authorization_fields(msg.active))
    await _confirm_properties(
        "confirm_newaccount",
        TR.tr("eos__new_account"),
        props,
    )


async def confirm_action_unknown(action: EosActionCommon, checksum: bytes) -> None:
    await confirm_properties(
        "confirm_unknown",
        TR.tr("eos__arbitrary_data"),
        (
            (TR.tr("eos__contract"), eos_name_to_string(action.account)),
            (TR.tr("eos__action_name"), eos_name_to_string(action.name)),
            (TR.tr("eos__checksum"), checksum),
        ),
        hold=is_last,
        br_code=ButtonRequestType.ConfirmOutput,
    )


def authorization_fields(auth: EosAuthorization) -> list[PropertyType]:
    from trezor.wire import DataError

    from ..helpers import public_key_to_wif

    fields: list[PropertyType] = []
    append = fields.append  # local_cache_attribute

    append((TR.tr("eos__threshold"), str(auth.threshold)))

    # NOTE: getting rid of f-strings saved almost 100 bytes

    for i, key in enumerate(auth.keys, 1):
        if key.key is None:
            raise DataError("Key must be provided explicitly.")

        _key = public_key_to_wif(bytes(key.key))
        _weight = str(key.weight)

        header = "Key #" + str(i) + ":"
        w_header = "Key #" + str(i) + " Weight:"

        append((header, _key))
        append((w_header, _weight))

    for i, account in enumerate(auth.accounts, 1):
        _account = eos_name_to_string(account.account.actor)
        _permission = eos_name_to_string(account.account.permission)

        i = str(i)
        # TODO: handle translation
        a_header = "Account #" + i + ":"
        p_header = "Acc Permission #" + i + ":"
        w_header = "Account #" + i + " weight:"

        append((a_header, _account))
        append((p_header, _permission))
        append((w_header, str(account.weight)))

    for i, wait in enumerate(auth.waits, 1):
        _wait = str(wait.wait_sec)
        _weight = str(wait.weight)

        header = "Delay #" + str(i)
        w_header = header + " weight:"
        append((header, _wait + " sec"))
        append((w_header, _weight))

    return fields
