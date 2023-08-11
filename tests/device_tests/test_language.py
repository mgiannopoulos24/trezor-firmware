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

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest

from trezorlib import device, exceptions, translations
from trezorlib.debuglink import TrezorClientDebugLink as Client

pytestmark = pytest.mark.skip_t1

HERE = Path(__file__).parent.resolve()
CORE = HERE.parent.parent / "core"
TRANSLATIONS = CORE / "embed" / "rust" / "src" / "ui" / "translations"

CS_JSON = TRANSLATIONS / "cs.json"
FR_JSON = TRANSLATIONS / "fr.json"

MOCK_LANG_DATA = "abc*def*".encode()
MAX_LENGTH = 32 * 1024


@contextmanager
def _set_english_return_back(client: Client) -> Generator[Client, None, None]:
    lang_before = client.features.language or ""
    try:
        with client:
            device.change_language(client, language="", language_data=b"")
        yield client
    finally:
        if lang_before.startswith("en"):
            with client:
                device.change_language(client, language="", language_data=b"")
        elif lang_before == "cs":
            with client, open(CS_JSON, "r") as f:
                language_data = translations.blob_from_file(f)
                device.change_language(
                    client, language="cs", language_data=language_data
                )
        elif lang_before == "fr":
            with client, open(FR_JSON, "r") as f:
                language_data = translations.blob_from_file(f)
                device.change_language(
                    client, language="fr", language_data=language_data
                )
        else:
            raise RuntimeError(f"Unknown language: {lang_before}")


def test_change_language(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # Setting cs language
        with client:
            device.change_language(client, language="cs", language_data=MOCK_LANG_DATA)
        assert client.features.language == "cs"

        # Setting the default language via empty data
        with client:
            device.change_language(client, language="", language_data=b"")
        assert client.features.language == "en-US"

        # Max length is accepted
        with client:
            device.change_language(
                client, language="cs", language_data=b"a" * MAX_LENGTH
            )
        assert client.features.language == "cs"


def test_change_language_errors(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # Language name too long
        with pytest.raises(
            exceptions.TrezorFailure, match="Language identifier too long"
        ), client:
            device.change_language(
                client, language=10 * "abcd", language_data=MOCK_LANG_DATA
            )
        assert client.features.language == "en-US"

        # Translations too long
        with pytest.raises(
            exceptions.TrezorFailure, match="Translations too long"
        ), client:
            device.change_language(
                client, language="cs", language_data=(MAX_LENGTH + 1) * b"a"
            )
        assert client.features.language == "en-US"


def test_full_language_change(client: Client):
    with _set_english_return_back(client) as client:
        assert client.features.language == "en-US"

        # Setting cs language
        with client, open(CS_JSON, "r") as f:
            language_data = translations.blob_from_file(f)
            device.change_language(client, language="cs", language_data=language_data)
        assert client.features.language == "cs"

        # Setting fr language
        with client, open(FR_JSON, "r") as f:
            language_data = translations.blob_from_file(f)
            device.change_language(client, language="fr", language_data=language_data)
        assert client.features.language == "fr"

        # Setting the default language via empty data
        with client:
            device.change_language(client, language="", language_data=b"")
        assert client.features.language == "en-US"
