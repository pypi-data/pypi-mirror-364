/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"

extern const char *param_must_be_seq;
extern const char *unreachable_code;
extern const char *non_string_seq;

namespace PyAttributeProxy
{
struct PickleSuite : bopy::pickle_suite
{
    static bopy::tuple getinitargs(Tango::AttributeProxy &self)
    {
        Tango::DeviceProxy *dev = self.get_device_proxy();

        std::string ret = dev->get_db_host() + ":" + dev->get_db_port() + "/" + dev->dev_name() + "/" + self.name();
        return bopy::make_tuple(ret);
    }
};

static boost::shared_ptr<Tango::AttributeProxy> makeAttributeProxy1(const std::string &name)
{
    AutoPythonAllowThreads guard;
    return boost::shared_ptr<Tango::AttributeProxy>(new Tango::AttributeProxy(name.c_str()), DeleterWithoutGIL());
}

static boost::shared_ptr<Tango::AttributeProxy> makeAttributeProxy2(const Tango::DeviceProxy *dev,
                                                                    const std::string &name)
{
    AutoPythonAllowThreads guard;
    return boost::shared_ptr<Tango::AttributeProxy>(new Tango::AttributeProxy(dev, name.c_str()), DeleterWithoutGIL());
}
} // namespace PyAttributeProxy

void export_attribute_proxy()
{
    bopy::class_<Tango::AttributeProxy> AttributeProxy("__AttributeProxy", bopy::init<const Tango::AttributeProxy &>());

    AttributeProxy.def("__init__", bopy::make_constructor(PyAttributeProxy::makeAttributeProxy1))
        .def("__init__", bopy::make_constructor(PyAttributeProxy::makeAttributeProxy2))

        //
        // Pickle
        //
        .def_pickle(PyAttributeProxy::PickleSuite())

        //
        // general methods
        //

        .def("name", &Tango::AttributeProxy::name, (arg_("self")))

        .def("get_device_proxy",
             &Tango::AttributeProxy::get_device_proxy,
             (arg_("self")),
             bopy::return_internal_reference<1>())

        //
        // property methods
        //
        .def("_get_property",
             (void(Tango::AttributeProxy::*)(const std::string &, Tango::DbData &)) &
                 Tango::AttributeProxy::get_property,
             (arg_("self"), arg_("propname"), arg_("propdata")))

        .def("_get_property",
             (void(Tango::AttributeProxy::*)(const std::vector<std::string> &, Tango::DbData &)) &
                 Tango::AttributeProxy::get_property,
             (arg_("self"), arg_("propnames"), arg_("propdata")))

        .def("_get_property",
             (void(Tango::AttributeProxy::*)(Tango::DbData &)) & Tango::AttributeProxy::get_property,
             (arg_("self"), arg_("propdata")))

        .def("_put_property", &Tango::AttributeProxy::put_property, (arg_("self"), arg_("propdata")))

        .def("_delete_property",
             (void(Tango::AttributeProxy::*)(const std::string &)) & Tango::AttributeProxy::delete_property,
             (arg_("self"), arg_("propname")))

        .def("_delete_property",
             (void(Tango::AttributeProxy::*)(const StdStringVector &)) & Tango::AttributeProxy::delete_property,
             (arg_("self"), arg_("propnames")))

        .def("_delete_property",
             (void(Tango::AttributeProxy::*)(const Tango::DbData &)) & Tango::AttributeProxy::delete_property,
             (arg_("self"), arg_("propdata")));
}
