/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_attribute_info_ex()
{
    bopy::class_<Tango::AttributeInfoEx, bopy::bases<Tango::AttributeInfo>>("AttributeInfoEx")
        .def(bopy::init<const Tango::AttributeInfoEx &>())
        .enable_pickling()
        .def_readwrite("root_attr_name", &Tango::AttributeInfoEx::root_attr_name)
        .def_readwrite("memorized", &Tango::AttributeInfoEx::memorized)
        .def_readwrite("enum_labels", &Tango::AttributeInfoEx::enum_labels)
        .def_readwrite("alarms", &Tango::AttributeInfoEx::alarms)
        .def_readwrite("events", &Tango::AttributeInfoEx::events)
        .def_readwrite("sys_extensions", &Tango::AttributeInfoEx::sys_extensions);
}
