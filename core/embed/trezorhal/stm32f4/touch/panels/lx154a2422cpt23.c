/*
 * This file is part of the Trezor project, https://trezor.io/
 *
 * Copyright (c) SatoshiLabs
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include TREZOR_BOARD

#include "lx154a2422cpt23.h"

#include "touch.h"

uint32_t lx154a2422cpt23_touch_correction(uint32_t event) {
#define CORRECTION_AT_EDGE 30
#define CENTER (DISPLAY_RESX / 2)

  int16_t x_old = touch_unpack_x(event);
  int16_t y_old = touch_unpack_y(event);

  int16_t x_dist_from_center =
      (x_old > CENTER) ? (x_old - CENTER) : (CENTER - x_old);

  int16_t x_correction = (x_dist_from_center * CORRECTION_AT_EDGE) / CENTER;

  int16_t x_new = x_old > CENTER ? x_old + x_correction : x_old - x_correction;

  if (x_new < 0) {
    x_new = 0;
  } else if (x_new >= DISPLAY_RESX) {
    x_new = DISPLAY_RESX - 1;
  }

  uint32_t new_coords = touch_pack_xy(x_new, y_old);

  event = (event & TOUCH_EVENT_MASK) | new_coords;

  return event;
}
