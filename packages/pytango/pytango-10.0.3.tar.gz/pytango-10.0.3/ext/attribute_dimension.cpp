/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_attribute_dimension()
{
    bopy::class_<Tango::AttributeDimension>("AttributeDimension")
        .def_readonly("dim_x", &Tango::AttributeDimension::dim_x)
        .def_readonly("dim_y", &Tango::AttributeDimension::dim_y);
}
