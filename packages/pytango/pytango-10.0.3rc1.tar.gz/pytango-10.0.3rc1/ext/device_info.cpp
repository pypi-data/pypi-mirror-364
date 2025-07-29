/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

#include <boost/python/suite/indexing/map_indexing_suite.hpp>

namespace PyDeviceInfo
{

bopy::dict get_version_info_dict(Tango::DeviceInfo &dev_info)
{
    bopy::dict info_dict;
    for(const auto &pair : dev_info.version_info)
    {
        info_dict[pair.first] = pair.second;
    }
    return info_dict;
}
} // namespace PyDeviceInfo

void export_device_info()
{
    bopy::class_<Tango::DeviceInfo>("DeviceInfo")
        .def_readonly("dev_class", &Tango::DeviceInfo::dev_class)
        .def_readonly("server_id", &Tango::DeviceInfo::server_id)
        .def_readonly("server_host", &Tango::DeviceInfo::server_host)
        .def_readonly("server_version", &Tango::DeviceInfo::server_version)
        .def_readonly("doc_url", &Tango::DeviceInfo::doc_url)
        .def_readonly("dev_type", &Tango::DeviceInfo::dev_type)
        .add_property("version_info", &PyDeviceInfo::get_version_info_dict);
}
