/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_attribute_alarm_info()
{
    bopy::class_<Tango::AttributeAlarmInfo>("AttributeAlarmInfo")
        .enable_pickling()
        .def_readwrite("min_alarm", &Tango::AttributeAlarmInfo::min_alarm)
        .def_readwrite("max_alarm", &Tango::AttributeAlarmInfo::max_alarm)
        .def_readwrite("min_warning", &Tango::AttributeAlarmInfo::min_warning)
        .def_readwrite("max_warning", &Tango::AttributeAlarmInfo::max_warning)
        .def_readwrite("delta_t", &Tango::AttributeAlarmInfo::delta_t)
        .def_readwrite("delta_val", &Tango::AttributeAlarmInfo::delta_val)
        .def_readwrite("extensions", &Tango::AttributeAlarmInfo::extensions);
}
