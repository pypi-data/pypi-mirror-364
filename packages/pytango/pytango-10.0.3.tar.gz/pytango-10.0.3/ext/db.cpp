/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"

void export_database();

namespace PyDbServerData
{

static inline bopy::str get_name(Tango::DbServerData &self)
{
    return bopy::str(self.get_name());
}

}; // namespace PyDbServerData

void export_db()
{
    // Note: DbDatum in python is extended to support the python sequence API
    //       in the file ../PyTango/db.py. This way the DbDatum behaves like a
    //       sequence of strings. This allows the user to work with a DbDatum as
    //       if it was working with the old list of strings

    bopy::class_<Tango::DbDatum>("DbDatum", bopy::init<>())
        .def(bopy::init<const char *>())
        .def(bopy::init<const Tango::DbDatum &>())
        .def_readwrite("name", &Tango::DbDatum::name)
        .def_readwrite("value_string", &Tango::DbDatum::value_string)
        .def("size", &Tango::DbDatum::size)
        .def("is_empty", &Tango::DbDatum::is_empty);

    bopy::class_<Tango::DbDevExportInfo>("DbDevExportInfo")
        .def_readwrite("name", &Tango::DbDevExportInfo::name)
        .def_readwrite("ior", &Tango::DbDevExportInfo::ior)
        .def_readwrite("host", &Tango::DbDevExportInfo::host)
        .def_readwrite("version", &Tango::DbDevExportInfo::version)
        .def_readwrite("pid", &Tango::DbDevExportInfo::pid);

    bopy::class_<Tango::DbDevImportInfo>("DbDevImportInfo")
        .def_readonly("name", &Tango::DbDevImportInfo::name)
        .def_readonly("exported", &Tango::DbDevImportInfo::exported)
        .def_readonly("ior", &Tango::DbDevImportInfo::ior)
        .def_readonly("version", &Tango::DbDevImportInfo::version);

    bopy::class_<Tango::DbDevFullInfo, bopy::bases<Tango::DbDevImportInfo>>("DbDevFullInfo")
        .def_readonly("class_name", &Tango::DbDevFullInfo::class_name)
        .def_readonly("ds_full_name", &Tango::DbDevFullInfo::ds_full_name)
        .def_readonly("started_date", &Tango::DbDevFullInfo::started_date)
        .def_readonly("stopped_date", &Tango::DbDevFullInfo::stopped_date)
        .def_readonly("pid", &Tango::DbDevFullInfo::pid);

    bopy::class_<Tango::DbDevInfo>("DbDevInfo")
        .def_readwrite("name", &Tango::DbDevInfo::name)
        .def_readwrite("_class", &Tango::DbDevInfo::_class)
        .def_readwrite("klass", &Tango::DbDevInfo::_class)
        .def_readwrite("server", &Tango::DbDevInfo::server);

    bopy::class_<Tango::DbHistory>("DbHistory", bopy::init<std::string, std::string, StdStringVector &>())
        .def(bopy::init<std::string, std::string, std::string, StdStringVector &>())
        .def("get_name", &Tango::DbHistory::get_name)
        .def("get_attribute_name", &Tango::DbHistory::get_attribute_name)
        .def("get_date", &Tango::DbHistory::get_date)
        .def("get_value", &Tango::DbHistory::get_value)
        .def("is_deleted", &Tango::DbHistory::is_deleted);

    bopy::class_<Tango::DbServerInfo>("DbServerInfo")
        .def_readwrite("name", &Tango::DbServerInfo::name)
        .def_readwrite("host", &Tango::DbServerInfo::host)
        .def_readwrite("mode", &Tango::DbServerInfo::mode)
        .def_readwrite("level", &Tango::DbServerInfo::level);

    bopy::class_<Tango::DbServerData>("DbServerData", bopy::init<const std::string, const std::string>())
        .def("get_name", &PyDbServerData::get_name)
        .def("put_in_database", &Tango::DbServerData::put_in_database)
        .def("already_exist", &Tango::DbServerData::already_exist)
        .def("remove", (void(Tango::DbServerData::*)()) & Tango::DbServerData::remove)
        .def("remove", (void(Tango::DbServerData::*)(const std::string &)) & Tango::DbServerData::remove);

    export_database();
}
