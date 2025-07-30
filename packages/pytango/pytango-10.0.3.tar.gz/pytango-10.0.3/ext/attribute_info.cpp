/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_attribute_info()
{
    bopy::class_<Tango::AttributeInfo, bopy::bases<Tango::DeviceAttributeConfig>>("AttributeInfo")
        .def(bopy::init<const Tango::AttributeInfo &>())
        .enable_pickling()
        .def_readwrite("disp_level", &Tango::AttributeInfo::disp_level);
}
