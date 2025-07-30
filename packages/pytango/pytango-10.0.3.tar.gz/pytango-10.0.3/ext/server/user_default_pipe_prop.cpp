/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

void export_user_default_pipe_prop()
{
    bopy::class_<Tango::UserDefaultPipeProp, boost::noncopyable>("UserDefaultPipeProp")
        .def("set_label", &Tango::UserDefaultPipeProp::set_label)
        .def("set_description", &Tango::UserDefaultPipeProp::set_description);
}
