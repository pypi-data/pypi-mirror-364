/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>

struct PyLockerInfo
{
    static inline bopy::object get_locker_id(Tango::LockerInfo &li)
    {
        return (li.ll == Tango::CPP) ? bopy::object(li.li.LockerPid) : bopy::tuple(li.li.UUID);
    }
};

void export_locker_info()
{
    bopy::class_<Tango::LockerInfo>("LockerInfo")
        .def_readonly("ll", &Tango::LockerInfo::ll)
        .add_property("li", &PyLockerInfo::get_locker_id)
        .def_readonly("locker_host", &Tango::LockerInfo::locker_host)
        .def_readonly("locker_class", &Tango::LockerInfo::locker_class);
}
