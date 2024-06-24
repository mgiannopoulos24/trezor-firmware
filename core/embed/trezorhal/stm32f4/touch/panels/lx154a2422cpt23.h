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

#ifndef TREZORHAL_TOUCH_LX154A2422CPT23_H
#define TREZORHAL_TOUCH_LX154A2422CPT23_H

#include <stdint.h>

// Performs touch coordinates correction needed for a specific panel
// The event parameter is a packed touch event, with event type and coordinates
// The return value is the corrected touch event with updated coordinates
//
// In case of LX154A2422CPT23, this correction means to shift X coordinate
// towards the edge of the screen, proportionally to the distance from the
// center of the screen.
uint32_t lx154a2422cpt23_touch_correction(uint32_t event);

#endif
