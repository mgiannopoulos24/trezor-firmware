from typing import TYPE_CHECKING, Sequence

import trezortranslate as TR
from trezor.enums import ButtonRequestType
from trezor.strings import format_amount
from trezor.ui.layouts import confirm_properties

from .helpers import DECIMALS

if TYPE_CHECKING:
    from trezor.messages import (
        BinanceCancelMsg,
        BinanceInputOutput,
        BinanceOrderMsg,
        BinanceTransferMsg,
    )


async def require_confirm_transfer(msg: BinanceTransferMsg) -> None:
    items: list[tuple[str, str, str]] = []

    def make_input_output_pages(msg: BinanceInputOutput, direction: str) -> None:
        for coin in msg.coins:
            items.append(
                (
                    direction,
                    format_amount(coin.amount, DECIMALS) + " " + coin.denom,
                    msg.address,
                )
            )

    for txinput in msg.inputs:
        make_input_output_pages(txinput, TR.tr("binance__confirm_input"))

    for txoutput in msg.outputs:
        make_input_output_pages(txoutput, TR.tr("binance__confirm_output"))

    await _confirm_transfer(items, chunkify=bool(msg.chunkify))


async def _confirm_transfer(
    inputs_outputs: Sequence[tuple[str, str, str]], chunkify: bool
) -> None:
    from trezor.ui.layouts import confirm_output

    for index, (title, amount, address) in enumerate(inputs_outputs):
        # Having hold=True on the last item
        hold = index == len(inputs_outputs) - 1
        await confirm_output(address, amount, title, hold=hold, chunkify=chunkify)


async def require_confirm_cancel(msg: BinanceCancelMsg) -> None:
    await confirm_properties(
        "confirm_cancel",
        TR.tr("binance__confirm_cancel"),
        (
            (TR.tr("binance__sender_address"), str(msg.sender)),
            (TR.tr("binance__pair"), str(msg.symbol)),
            (TR.tr("binance__order_id"), str(msg.refid)),
        ),
        hold=True,
        br_code=ButtonRequestType.SignTx,
    )


async def require_confirm_order(msg: BinanceOrderMsg) -> None:
    from trezor.enums import BinanceOrderSide

    if msg.side == BinanceOrderSide.BUY:
        side = TR.tr("binance__buy")
    elif msg.side == BinanceOrderSide.SELL:
        side = TR.tr("binance__sell")
    else:
        side = TR.tr("binance__unknown")

    await confirm_properties(
        "confirm_order",
        TR.tr("binance__confirm_order"),
        (
            (TR.tr("binance__sender_address"), str(msg.sender)),
            (TR.tr("binance__pair"), str(msg.symbol)),
            (TR.tr("binance__side"), side),
            (TR.tr("binance__quantity"), format_amount(msg.quantity, DECIMALS)),
            (TR.tr("binance__price"), format_amount(msg.price, DECIMALS)),
        ),
        hold=True,
        br_code=ButtonRequestType.SignTx,
    )
