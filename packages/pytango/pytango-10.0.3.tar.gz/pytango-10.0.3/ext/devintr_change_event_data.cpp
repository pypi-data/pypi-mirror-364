/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

#include "exception.h"

extern bopy::object PyTango_DevFailed;

namespace PyDevIntrChangeEventData
{
static boost::shared_ptr<Tango::DevIntrChangeEventData> makeDevIntrChangeEventData()
{
    Tango::DevIntrChangeEventData *result = new Tango::DevIntrChangeEventData;
    return boost::shared_ptr<Tango::DevIntrChangeEventData>(result);
}

static void set_errors(Tango::DevIntrChangeEventData &event_data, bopy::object &dev_failed)
{
    Tango::DevFailed df;
    bopy::object errors = dev_failed.attr("args");
    sequencePyDevError_2_DevErrorList(errors.ptr(), event_data.errors);
}

}; // namespace PyDevIntrChangeEventData

void export_devintr_change_event_data()
{
    bopy::class_<Tango::DevIntrChangeEventData>("DevIntrChangeEventData",
                                                bopy::init<const Tango::DevIntrChangeEventData &>())

        .def("__init__", bopy::make_constructor(PyDevIntrChangeEventData::makeDevIntrChangeEventData))
        // The original Tango::DevIntrChangeEventData structure has a 'device' field.
        // However, if we returned this directly we would get a different
        // python device each time. So we are doing our weird things to make
        // sure the device returned is the same where the read action was
        // performed. So we don't return Tango::DevIntrChangeEventData::device directly.
        // See callback.cpp
        .setattr("device", bopy::object())
        .def_readwrite("event", &Tango::DevIntrChangeEventData::event)
        .def_readwrite("device_name", &Tango::DevIntrChangeEventData::device_name)

        .setattr("cmd_list", bopy::object())
        .setattr("att_list", bopy::object())
        .def_readwrite("dev_started", &Tango::DevIntrChangeEventData::dev_started)

        .def_readwrite("err", &Tango::DevIntrChangeEventData::err)
        .def_readwrite("reception_date", &Tango::DevIntrChangeEventData::reception_date)

        .def_readwrite("err", &Tango::DevIntrChangeEventData::err)
        .add_property("errors",
                      bopy::make_getter(&Tango::DevIntrChangeEventData::errors,
                                        bopy::return_value_policy<bopy::copy_non_const_reference>()),
                      &PyDevIntrChangeEventData::set_errors)
        .def("get_date", &Tango::DevIntrChangeEventData::get_date, bopy::return_internal_reference<>());
}
