/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

#include "exception.h"

extern bopy::object PyTango_DevFailed;

namespace PyEventData
{
static boost::shared_ptr<Tango::EventData> makeEventData()
{
    Tango::EventData *result = new Tango::EventData;
    result->attr_value = new Tango::DeviceAttribute();
    return boost::shared_ptr<Tango::EventData>(result);
}

static void set_errors(Tango::EventData &event_data, bopy::object &error)
{
    PyObject *error_ptr = error.ptr();
    if(PyObject_IsInstance(error_ptr, PyTango_DevFailed.ptr()))
    {
        Tango::DevFailed df;
        bopy::object error_list = error.attr("args");
        sequencePyDevError_2_DevErrorList(error_list.ptr(), event_data.errors);
    }
    else
    {
        sequencePyDevError_2_DevErrorList(error_ptr, event_data.errors);
    }
}
}; // namespace PyEventData

void export_event_data()
{
    bopy::class_<Tango::EventData>("EventData", bopy::init<const Tango::EventData &>())

        .def("__init__", bopy::make_constructor(PyEventData::makeEventData))

        // The original Tango::EventData structure has a 'device' field.
        // However, if we returned this directly we would get a different
        // python device each time. So we are doing our weird things to make
        // sure the device returned is the same where the read action was
        // performed. So we don't return Tango::EventData::device directly.
        // See callback.cpp
        .setattr("device", bopy::object())

        .def_readwrite("attr_name", &Tango::EventData::attr_name)
        .def_readwrite("event", &Tango::EventData::event)

        // The original Tango::EventData structure has "get_attr_value" but
        // we can't refer it directly here because we have to extract value
        // and so on.
        // See callback.cpp
        .setattr("attr_value", bopy::object())

        .def_readwrite("err", &Tango::EventData::err)
        .def_readwrite("reception_date", &Tango::EventData::reception_date)
        .add_property(
            "errors",
            make_getter(&Tango::EventData::errors, bopy::return_value_policy<bopy::copy_non_const_reference>()),
            &PyEventData::set_errors)

        .def("get_date", &Tango::EventData::get_date, bopy::return_internal_reference<>());
}
