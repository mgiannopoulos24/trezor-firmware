
#include <stdint.h>
#include "secbool.h"

void translations_write(uint8_t* data, uint32_t offset, uint32_t len);

const uint8_t* translations_read(uint32_t* len);

void translations_erase(void);
