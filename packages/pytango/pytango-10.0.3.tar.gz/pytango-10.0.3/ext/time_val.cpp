/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_time_val()
{
    bopy::class_<Tango::TimeVal>("TimeVal")
        .def_readwrite("tv_sec", &Tango::TimeVal::tv_sec)
        .def_readwrite("tv_usec", &Tango::TimeVal::tv_usec)
        .def_readwrite("tv_nsec", &Tango::TimeVal::tv_nsec);
}
