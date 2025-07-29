/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "pytgutils.h"

void export_multi_class_attribute()
{
    bopy::class_<Tango::MultiClassAttribute, boost::noncopyable>("MultiClassAttribute", bopy::no_init)
        .def("get_attr",
             (Tango::Attr & (Tango::MultiClassAttribute::*) (const std::string &) ) &
                 Tango::MultiClassAttribute::get_attr,
             bopy::return_value_policy<bopy::reference_existing_object>())
        .def("remove_attr", &Tango::MultiClassAttribute::remove_attr)
        .def("get_attr_list",
             &Tango::MultiClassAttribute::get_attr_list,
             bopy::return_value_policy<bopy::reference_existing_object>());
}
