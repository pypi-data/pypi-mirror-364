/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_user_default_fwdattr_prop()
{
    bopy::class_<Tango::UserDefaultFwdAttrProp, boost::noncopyable>("UserDefaultFwdAttrProp")
        .def("set_label", &Tango::UserDefaultFwdAttrProp::set_label);
}

void export_fwdattr()
{
    bopy::class_<Tango::FwdAttr, boost::noncopyable>("FwdAttr", bopy::init<const std::string &, const std::string &>())
        .def("set_default_properties", &Tango::FwdAttr::set_default_properties);
}
