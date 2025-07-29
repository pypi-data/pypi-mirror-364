/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_dev_command_info()
{
    typedef Tango::CmdArgType Tango::_DevCommandInfo::*MemCmdArgType;

    bopy::class_<Tango::DevCommandInfo>("DevCommandInfo")
        .def_readonly("cmd_name", &Tango::DevCommandInfo::cmd_name)
        .def_readonly("cmd_tag", &Tango::DevCommandInfo::cmd_tag)
        .def_readonly("in_type", reinterpret_cast<MemCmdArgType>(&Tango::DevCommandInfo::in_type))
        .def_readonly("out_type", reinterpret_cast<MemCmdArgType>(&Tango::DevCommandInfo::out_type))
        .def_readonly("in_type_desc", &Tango::DevCommandInfo::in_type_desc)
        .def_readonly("out_type_desc", &Tango::DevCommandInfo::out_type_desc);
}
