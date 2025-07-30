/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_device_data_history()
{
    bopy::class_<Tango::DeviceDataHistory, bopy::bases<Tango::DeviceData>> DeviceDataHistory("DeviceDataHistory",
                                                                                             bopy::init<>());

    DeviceDataHistory
        .def(bopy::init<const Tango::DeviceDataHistory &>())

        .def("has_failed", &Tango::DeviceDataHistory::has_failed)
        .def("get_date", &Tango::DeviceDataHistory::get_date, bopy::return_internal_reference<>())
        .def("get_err_stack",
             &Tango::DeviceDataHistory::get_err_stack,
             bopy::return_value_policy<bopy::copy_const_reference>());
}
