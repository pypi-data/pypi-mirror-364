/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#pragma once

#include <boost/python.hpp>
#include <tango/tango.h>

#include "defs.h"
#include "pyutils.h"

namespace PyTango
{
namespace DevicePipe
{
bopy::object extract(Tango::DevicePipeBlob &blob, PyTango::ExtractAs extract_as = PyTango::ExtractAsNumpy);

void update_values(Tango::DevicePipe &self,
                   bopy::object &py_value,
                   PyTango::ExtractAs extract_as = PyTango::ExtractAsNumpy);

template <typename TDevicePipe>
bopy::object convert_to_python(TDevicePipe *self, PyTango::ExtractAs extract_as)
{
    bopy::object py_value;
    try
    {
        py_value = bopy::object(
            bopy::handle<>(bopy::to_python_indirect<TDevicePipe *, bopy::detail::make_owning_holder>()(self)));
    }
    catch(...)
    {
        delete self;
        throw;
    }

    update_values(*self, py_value, extract_as);
    return py_value;
}
} // namespace DevicePipe
} // namespace PyTango
