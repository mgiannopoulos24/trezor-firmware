from typing import TYPE_CHECKING

import trezortranslate as TR

from ..layout import require_confirm_content, require_confirm_final

if TYPE_CHECKING:
    from trezor.messages import (
        NEMMosaicCreation,
        NEMMosaicDefinition,
        NEMMosaicSupplyChange,
        NEMTransactionCommon,
    )


async def ask_mosaic_creation(
    common: NEMTransactionCommon, creation: NEMMosaicCreation
) -> None:
    from ..layout import require_confirm_fee

    creation_message = [
        (TR.tr("nem__create_mosaic"), creation.definition.mosaic),
        (TR.tr("nem__under_namespace"), creation.definition.namespace),
    ]
    await require_confirm_content(TR.tr("nem__create_mosaic"), creation_message)
    await _require_confirm_properties(creation.definition)
    await require_confirm_fee(TR.tr("nem__confirm_creation_fee"), creation.fee)

    await require_confirm_final(common.fee)


async def ask_supply_change(
    common: NEMTransactionCommon, change: NEMMosaicSupplyChange
) -> None:
    from trezor.enums import NEMSupplyChangeType

    from ..layout import require_confirm_text

    supply_message = [
        (TR.tr("nem__modify_supply_for"), change.mosaic),
        (TR.tr("nem__under_namespace"), change.namespace),
    ]
    await require_confirm_content(TR.tr("nem__supply_change"), supply_message)
    if change.type == NEMSupplyChangeType.SupplyChange_Decrease:
        action = TR.tr("nem__decrease")
    elif change.type == NEMSupplyChangeType.SupplyChange_Increase:
        action = TR.tr("nem__increase")
    else:
        raise ValueError("Invalid supply change type")
    await require_confirm_text(
        TR.tr("nem__supply_units_template").format(action, change.delta)
    )

    await require_confirm_final(common.fee)


async def _require_confirm_properties(definition: NEMMosaicDefinition) -> None:
    from trezor.enums import NEMMosaicLevy
    from trezor.ui.layouts import confirm_properties

    properties = []
    append = properties.append  # local_cache_attribute

    # description
    if definition.description:
        append((TR.tr("nem__description"), definition.description))

    # transferable
    transferable = TR.tr("nem__yes") if definition.transferable else TR.tr("nem__no")
    append((TR.tr("nem__transferable"), transferable))

    # mutable_supply
    imm = (
        TR.tr("nem__mutable") if definition.mutable_supply else TR.tr("nem__immutable")
    )
    if definition.supply:
        append((TR.tr("nem__initial_supply"), str(definition.supply) + "\n" + imm))
    else:
        append((TR.tr("nem__initial_supply"), imm))

    # levy
    if definition.levy:
        # asserts below checked in nem.validators._validate_mosaic_creation
        assert definition.levy_address is not None
        assert definition.levy_namespace is not None
        assert definition.levy_mosaic is not None

        append((TR.tr("nem__levy_recipient"), definition.levy_address))

        append((TR.tr("nem__levy_fee"), str(definition.fee)))
        append((TR.tr("nem__levy_divisibility"), str(definition.divisibility)))

        append((TR.tr("nem__levy_namespace"), definition.levy_namespace))
        append((TR.tr("nem__levy_mosaic"), definition.levy_mosaic))

        levy_type = (
            TR.tr("nem__absolute")
            if definition.levy == NEMMosaicLevy.MosaicLevy_Absolute
            else TR.tr("nem__percentile")
        )
        append((TR.tr("nem__levy_type"), levy_type))

    await confirm_properties(
        "confirm_properties",
        TR.tr("nem__confirm_properties"),
        properties,
    )
