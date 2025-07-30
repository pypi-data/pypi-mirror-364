/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_attribute_event_info()
{
    bopy::class_<Tango::AttributeEventInfo>("AttributeEventInfo")
        .enable_pickling()
        .def_readwrite("ch_event", &Tango::AttributeEventInfo::ch_event)
        .def_readwrite("per_event", &Tango::AttributeEventInfo::per_event)
        .def_readwrite("arch_event", &Tango::AttributeEventInfo::arch_event);
}
