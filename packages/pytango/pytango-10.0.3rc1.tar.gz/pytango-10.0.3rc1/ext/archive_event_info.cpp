/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_archive_event_info()
{
    bopy::class_<Tango::ArchiveEventInfo>("ArchiveEventInfo")
        .enable_pickling()
        .def_readwrite("archive_rel_change", &Tango::ArchiveEventInfo::archive_rel_change)
        .def_readwrite("archive_abs_change", &Tango::ArchiveEventInfo::archive_abs_change)
        .def_readwrite("archive_period", &Tango::ArchiveEventInfo::archive_period)
        .def_readwrite("extensions", &Tango::ArchiveEventInfo::extensions);
}
