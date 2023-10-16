# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest

from trezorlib import debuglink, device, exceptions, translations
from trezorlib.debuglink import TrezorClientDebugLink as Client

pytestmark = pytest.mark.skip_t1

HERE = Path(__file__).parent.resolve()
CORE = HERE.parent.parent / "core"
TRANSLATIONS = CORE / "embed" / "rust" / "src" / "ui" / "translations"

CS_JSON = TRANSLATIONS / "cs.json"
FR_JSON = TRANSLATIONS / "fr.json"

MAX_DATA_LENGTH = 32 * 1024


@contextmanager
def _set_english_return_back(client: Client) -> Generator[Client, None, None]:
    lang_before = client.features.language or ""
    try:
        _set_default_english(client)
        yield client
    finally:
        if lang_before.startswith("en"):
            _set_default_english(client)
        elif lang_before == "cs":
            _set_full_czech(client)
        elif lang_before == "fr":
            _set_full_french(client)
        else:
            raise RuntimeError(f"Unknown language: {lang_before}")


def _set_full_czech(client: Client):
    with client, open(CS_JSON, "r") as f:
        device.change_language(client, language_data=translations.blob_from_file(f))


def _set_full_french(client: Client):
    with client, open(FR_JSON, "r") as f:
        device.change_language(client, language_data=translations.blob_from_file(f))


def _set_default_english(client: Client):
    with client:
        device.change_language(client, language_data=b"")


def test_change_language_errors(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # TODO: invalid header
        # TODO: invalid signature

        # Translations too short
        with pytest.raises(
            exceptions.TrezorFailure, match="Translations too short"
        ), client:
            device.change_language(client, language_data=10 * b"a")
        assert client.features.language == "en-US"

        # Translations too long
        with pytest.raises(
            exceptions.TrezorFailure, match="Translations too long"
        ), client:
            device.change_language(client, language_data=(MAX_DATA_LENGTH + 1) * b"a")
        assert client.features.language == "en-US"

        # Invalid header data length
        with pytest.raises(
            exceptions.TrezorFailure, match="Invalid header data length"
        ), client:
            with open(CS_JSON, "r") as f:
                device.change_language(
                    client, language_data=translations.blob_from_file(f) + b"abc"
                )
        assert client.features.language == "en-US"

        # Invalid data hash
        with pytest.raises(exceptions.TrezorFailure, match="Invalid data hash"), client:
            with open(CS_JSON, "r") as f:
                device.change_language(
                    client, language_data=translations.blob_from_file(f)[:-4] + b"abcd"
                )
        assert client.features.language == "en-US"

        # Invalid translations version
        with pytest.raises(
            exceptions.TrezorFailure, match="Invalid translations version"
        ), client:
            with open(CS_JSON, "r") as f:
                data = json.load(f)
            data["header"]["version"] = "3.5.4"
            device.change_language(
                client, language_data=translations.blob_from_dict(data)
            )
        assert client.features.language == "en-US"

        # Invalid header version
        with pytest.raises(
            exceptions.TrezorFailure, match="Invalid header version"
        ), client:
            with open(CS_JSON, "r") as f:
                data = json.load(f)
            data["header"]["version"] = "ABC.XYZ.DEF"
            device.change_language(
                client, language_data=translations.blob_from_dict(data)
            )
        assert client.features.language == "en-US"


def test_full_language_change(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # Setting cs language
        _set_full_czech(client)
        assert client.features.language == "cs"

        # Setting fr language
        _set_full_french(client)
        assert client.features.language == "fr"

        # Setting the default language via empty data
        _set_default_english(client)
        assert client.features.language == "en-US"


def test_language_stays_after_wipe(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # Setting cs language
        _set_full_czech(client)
        assert client.features.language == "cs"

        # Wipe device
        device.wipe(client)
        assert client.features.language == "cs"

        # Load it again
        debuglink.load_device(
            client,
            mnemonic=" ".join(["all"] * 12),
            pin=None,
            passphrase_protection=False,
            label="test",
        )
        assert client.features.language == "cs"
