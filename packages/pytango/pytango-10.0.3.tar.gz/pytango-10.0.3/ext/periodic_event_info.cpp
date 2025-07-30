/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_periodic_event_info()
{
    bopy::class_<Tango::PeriodicEventInfo>("PeriodicEventInfo")
        .enable_pickling()
        .def_readwrite("period", &Tango::PeriodicEventInfo::period)
        .def_readwrite("extensions", &Tango::PeriodicEventInfo::extensions);
}
