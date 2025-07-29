/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

namespace PySubDevDiag
{
PyObject *get_sub_devices(Tango::SubDevDiag &self)
{
    Tango::DevVarStringArray *sub_devs = self.get_sub_devices();

    bopy::list py_sub_devs;
    for(unsigned long i = 0; i < sub_devs->length(); ++i)
    {
        py_sub_devs.append((*sub_devs)[i].in());
    }
    delete sub_devs;
    return bopy::incref(py_sub_devs.ptr());
}
} // namespace PySubDevDiag

void export_sub_dev_diag()
{
    bopy::class_<Tango::SubDevDiag, boost::noncopyable>("SubDevDiag", bopy::no_init)
        .def("set_associated_device", &Tango::SubDevDiag::set_associated_device)
        .def("get_associated_device", &Tango::SubDevDiag::get_associated_device)
        .def("register_sub_device", &Tango::SubDevDiag::register_sub_device)
        .def("remove_sub_devices", (void(Tango::SubDevDiag::*)()) & Tango::SubDevDiag::remove_sub_devices)
        .def("remove_sub_devices", (void(Tango::SubDevDiag::*)(std::string)) & Tango::SubDevDiag::remove_sub_devices)
        .def("get_sub_devices", &PySubDevDiag::get_sub_devices)
        .def("store_sub_devices", &Tango::SubDevDiag::store_sub_devices)
        .def("get_sub_devices_from_cache", &Tango::SubDevDiag::get_sub_devices_from_cache);
}
