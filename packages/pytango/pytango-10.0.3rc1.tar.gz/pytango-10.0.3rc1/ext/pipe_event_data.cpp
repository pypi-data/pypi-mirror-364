/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

#include "exception.h"

extern bopy::object PyTango_DevFailed;

namespace PyPipeEventData
{
static boost::shared_ptr<Tango::PipeEventData> makePipeEventData()
{
    Tango::PipeEventData *result = new Tango::PipeEventData;
    return boost::shared_ptr<Tango::PipeEventData>(result);
}

static void set_errors(Tango::PipeEventData &event_data, bopy::object &dev_failed)
{
    Tango::DevFailed df;
    bopy::object errors = dev_failed.attr("args");
    sequencePyDevError_2_DevErrorList(errors.ptr(), event_data.errors);
}

}; // namespace PyPipeEventData

void export_pipe_event_data()
{
    bopy::class_<Tango::PipeEventData>("PipeEventData", bopy::init<const Tango::PipeEventData &>())

        .def("__init__", bopy::make_constructor(PyPipeEventData::makePipeEventData))
        // The original Tango::PipeEventData structure has a 'device' field.
        // However, if we returned this directly we would get a different
        // python device each time. So we are doing our weird things to make
        // sure the device returned is the same where the read action was
        // performed. So we don't return Tango::PipeEventData::device directly.
        // See callback.cpp
        .setattr("device", bopy::object())
        .def_readwrite("pipe_name", &Tango::PipeEventData::pipe_name)
        .def_readwrite("event", &Tango::PipeEventData::event)

        .setattr("pipe_value", bopy::object())

        .def_readwrite("err", &Tango::PipeEventData::err)
        .def_readwrite("reception_date", &Tango::PipeEventData::reception_date)
        .add_property(
            "errors",
            make_getter(&Tango::PipeEventData::errors, bopy::return_value_policy<bopy::copy_non_const_reference>()),
            &PyPipeEventData::set_errors)

        .def("get_date", &Tango::PipeEventData::get_date, bopy::return_internal_reference<>());
}
