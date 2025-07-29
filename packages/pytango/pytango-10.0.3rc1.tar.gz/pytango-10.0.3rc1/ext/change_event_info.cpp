/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_change_event_info()
{
    bopy::class_<Tango::ChangeEventInfo>("ChangeEventInfo")
        .enable_pickling()
        .def_readwrite("rel_change", &Tango::ChangeEventInfo::rel_change)
        .def_readwrite("abs_change", &Tango::ChangeEventInfo::abs_change)
        .def_readwrite("extensions", &Tango::ChangeEventInfo::extensions);
}
