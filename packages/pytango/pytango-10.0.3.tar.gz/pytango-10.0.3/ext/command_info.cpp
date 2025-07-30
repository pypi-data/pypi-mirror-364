/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_command_info()
{
    bopy::class_<Tango::CommandInfo, bopy::bases<Tango::DevCommandInfo>>("CommandInfo")
        .def_readonly("disp_level", &Tango::CommandInfo::disp_level);
}
