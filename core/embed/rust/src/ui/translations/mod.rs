mod en;
mod export;
mod general;

pub use en::EN_TRANSLATIONS;

use crate::{
    micropython::{buffer::StrBuffer, obj::Obj, util},
    trezorhal::storage::translations_get,
};

use core::str;

// Translations strings are delimited by a star
const DELIMITER_BYTE: u8 = b'*';
const TERMINATE_BYTE: u8 = 0xFF;

/// Translation function callable from micropython.
pub extern "C" fn translate_obj(key: Obj) -> Obj {
    let block = || {
        let str_key: StrBuffer = key.try_into()?;
        tr(&str_key).try_into()
    };
    unsafe { util::try_or_raise(block) }
}

/// Translation function for Rust.
pub fn tr(key: &str) -> &'static str {
    translate(key).unwrap_or_default()
}

/// Try to find the translation in flash (for a non-english language).
/// If not found, fallback to english.
fn translate(key: &str) -> Option<&'static str> {
    let mut translation: Option<&'static str> = None;

    if are_there_translations() {
        let chunk_len = 1024;
        let max_offset = 32 * 1024;
        if let Some(index) = EN_TRANSLATIONS.get_position(key) {
            translation = get_translation_by_index(index, chunk_len, max_offset);
        }
    }

    if translation.is_none() {
        translation = EN_TRANSLATIONS.get_text(key);
    }

    translation
}

/// Quickly checks whether there are some valid translations data
fn are_there_translations() -> bool {
    let first_byte_buffer: &'static [u8] = translations_get(0, 1).unwrap_or(&[]);
    first_byte_buffer[0] != TERMINATE_BYTE
}

/// Loops through all the translations data in flash and
/// returns the translation at the given index.
/// If there are no translations, it encounters TERMINATE_BYTE immediately
/// and returns None.
fn get_translation_by_index(index: usize, chunk_len: u32, max_offset: u32) -> Option<&'static str> {
    let mut current_index = 0;
    let mut offset = 0;
    let mut len = chunk_len;
    let mut chunk_start = 0;

    loop {
        // No more data to read
        if offset >= max_offset {
            return None;
        }
        // Reading the rest of the data
        if offset + len > max_offset {
            len = max_offset - offset;
        }

        let data_buffer: &'static [u8] = translations_get(offset, len).unwrap_or(&[]);
        offset += len;

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
        // The translation is split into two chunks, need to modify the offset and
        // chunk_start to read it all at once.
        if current_index == index {
            offset -= len - chunk_start as u32;
            chunk_start = 0;
        }
    }
}

// TODO: add some tests?
