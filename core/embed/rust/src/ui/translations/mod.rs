mod en;
#[cfg(feature = "micropython")]
mod export;
mod general;
#[cfg(feature = "micropython")]
mod micropython;

use en::EN_TRANSLATIONS;
use general::LANGUAGE_INDEX;

use crate::trezorhal::translations::translations_get;

use core::str;

// Translations strings are delimited by a star
const DELIMITER_BYTE: u8 = 0x00;
const TERMINATE_BYTE: u8 = 0xFF;

/// Translation function for Rust.
pub fn tr(key: &str) -> &'static str {
    translate(key).unwrap_or_default()
}

/// Get the language name.
fn get_language_name() -> Option<&'static str> {
    get_translation_by_index(LANGUAGE_INDEX)
}

/// Try to find the translation in flash (for a non-english language).
/// If not found, fallback to english.
fn translate(key: &str) -> Option<&'static str> {
    let mut translation: Option<&'static str> = None;

    if are_there_translations() {
        if let Some(index) = EN_TRANSLATIONS.get_position(key) {
            translation = get_translation_by_index(index);
        }
    }

    if translation.is_none() {
        translation = EN_TRANSLATIONS.get_text(key);
    }

    translation
}

/// Quickly checks whether there are some valid translations data
fn are_there_translations() -> bool {
    translations_get()[0] != TERMINATE_BYTE
}

/// Loops through all the translations data in flash and
/// returns the translation at the given index.
fn get_translation_by_index(index: usize) -> Option<&'static str> {
    let mut current_index = 0;
    let mut chunk_start = 0;

    let data_buffer = translations_get();

    for (i, &byte) in data_buffer.iter().enumerate() {
        if byte == TERMINATE_BYTE {
            return None;
        }
        if byte == DELIMITER_BYTE {
            if current_index == index {
                return str::from_utf8(&data_buffer[chunk_start..i]).ok();
            }
            chunk_start = i + 1;
            current_index += 1;
            continue;
        }
    }
    None
}

// TODO: add some tests?
