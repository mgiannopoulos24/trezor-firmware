use super::ffi;

pub fn translations_get() -> &'static [u8] {
    let mut len: u32 = 0;
    let ptr = unsafe { ffi::translations_read(&mut len) };
    if ptr.is_null() {
        fatal_error!("Translations read failed", "");
    }
    unsafe { core::slice::from_raw_parts(ptr, len as usize) }
}
