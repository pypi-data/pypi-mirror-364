/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

#include "exception.h"

extern bopy::object PyTango_DevFailed;

struct PyDataReadyEventData
{
    static inline Tango::DeviceProxy *get_device(Tango::DataReadyEventData &_self)
    {
        return _self.device;
    }

    static boost::shared_ptr<Tango::DataReadyEventData> makeDataReadyEventData()
    {
        Tango::DataReadyEventData *result = new Tango::DataReadyEventData;
        return boost::shared_ptr<Tango::DataReadyEventData>(result);
    }

    static void set_errors(Tango::DataReadyEventData &event_data, bopy::object &dev_failed)
    {
        Tango::DevFailed df;
        bopy::object errors = dev_failed.attr("args");
        sequencePyDevError_2_DevErrorList(errors.ptr(), event_data.errors);
    }
};

void export_data_ready_event_data()
{
    bopy::class_<Tango::DataReadyEventData>("DataReadyEventData", bopy::init<const Tango::DataReadyEventData &>())

        .def("__init__", bopy::make_constructor(PyDataReadyEventData::makeDataReadyEventData))

        // The original Tango::EventData structure has a 'device' field.
        // However, if we returned this directly we would get a different
        // python device each time. So we are doing our weird things to make
        // sure the device returned is the same where the read action was
        // performed. So we don't return Tango::EventData::device directly.
        // See callback.cpp
        .setattr("device", bopy::object())
        .def_readwrite("attr_name", &Tango::DataReadyEventData::attr_name)
        .def_readwrite("event", &Tango::DataReadyEventData::event)
        .def_readwrite("attr_data_type", &Tango::DataReadyEventData::attr_data_type)
        .def_readwrite("ctr", &Tango::DataReadyEventData::ctr)
        .def_readwrite("err", &Tango::DataReadyEventData::err)
        .def_readwrite("reception_date", &Tango::DataReadyEventData::reception_date)
        .add_property("errors",
                      bopy::make_getter(&Tango::DataReadyEventData::errors,
                                        bopy::return_value_policy<bopy::copy_non_const_reference>()),
                      &PyDataReadyEventData::set_errors)

        .def("get_date", &Tango::DataReadyEventData::get_date, bopy::return_internal_reference<>());
}
