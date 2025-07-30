/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_pipe_info()
{
    bopy::class_<Tango::PipeInfo>("PipeInfo")
        .def(bopy::init<const Tango::PipeInfo &>())
        .enable_pickling()
        .def_readwrite("name", &Tango::PipeInfo::name)
        .def_readwrite("description", &Tango::PipeInfo::description)
        .def_readwrite("label", &Tango::PipeInfo::label)
        .def_readwrite("disp_level", &Tango::PipeInfo::disp_level)
        .def_readwrite("writable", &Tango::PipeInfo::writable)
        .def_readwrite("extensions", &Tango::PipeInfo::extensions);
}
