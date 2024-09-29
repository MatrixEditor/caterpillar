/**
 * Copyright (C) MatrixEditor 2024
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
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#ifndef CP_DEFAULT_H
#define CP_DEFAULT_H

#include "caterpillarapi.h"

/* immortal objects */

#define CpInvalidDefault (&_CpInvalidDefault_Object)
#define Cp_IsInvalidDefault(o) ((o) == CpInvalidDefault)

#define CpDefaultOption (&_CpDefaultOption_Object)
#define Cp_IsDefaultOption(o) ((o) == CpDefaultOption)

#endif