/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_poll_device()
{
    bopy::class_<Tango::PollDevice>("PollDevice",
                                    "A structure containing PollDevice information\n"
                                    "the following members,\n"
                                    " - dev_name : string\n"
                                    " - ind_list : sequence<long>\n"
                                    "\nNew in PyTango 7.0.0")
        .def_readwrite("dev_name", &Tango::PollDevice::dev_name)
        .def_readwrite("ind_list", &Tango::PollDevice::ind_list);
}
