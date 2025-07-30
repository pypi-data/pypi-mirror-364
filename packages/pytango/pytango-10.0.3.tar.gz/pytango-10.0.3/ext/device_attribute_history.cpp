/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>
#include "pyutils.h"

void export_device_attribute_history()
{
    bopy::class_<Tango::DeviceAttributeHistory, bopy::bases<Tango::DeviceAttribute>> DeviceAttributeHistory(
        "DeviceAttributeHistory", bopy::init<>());

    DeviceAttributeHistory.def(bopy::init<const Tango::DeviceAttributeHistory &>())
        .def("has_failed", &Tango::DeviceAttributeHistory::has_failed);
}
