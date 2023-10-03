//! generated from cs.rs.mako
//! (by running `make templates` in `core`)
//! do not edit manually!

<%
import json
from pathlib import Path

THIS = Path(local.filename).resolve()
SRCDIR = THIS.parent

en_file = SRCDIR / "en.json"
en_data = json.loads(en_file.read_text())

def get_all_json_keys(data: dict) -> set[str]:
    keys: set[str] = set()
    for section_name, section in data.items():
        for k, v in section.items():
            keys.add(f"{section_name}__{k}")
    return keys

en_keys = get_all_json_keys(en_data)
%>\
use crate::micropython::{map::Map, module::Module, qstr::Qstr};

use super::{language_name_obj, translate_obj};

#[no_mangle]
#[rustfmt::skip]
pub static mp_module_trezortranslate: Module = obj_module! {
    // TODO: add function to get all the translations keys in order
    // - so that client can validate it is sending correct keys in correct order

    /// def language_name() -> str:
    ///     """Get the name of the current language."""
    Qstr::MP_QSTR_language_name => obj_fn_0!(language_name_obj).as_obj(),

    /// def tr(key: Literal[
% for name in sorted(en_keys):
    ///     ${utf8_str(name)},
% endfor
    /// ]) -> str:
    ///     """Get translation in the current language."""
    Qstr::MP_QSTR_tr => obj_fn_1!(translate_obj).as_obj(),
};
