/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include <tango/tango.h>
#include "pyutils.h"

namespace PyApiUtil
{
inline bopy::object get_env_var(const char *name)
{
    std::string value;
    if(Tango::ApiUtil::get_env_var(name, value) == 0)
    {
        return bopy::str(value);
    }
    return bopy::object();
}

inline void get_asynch_replies1(Tango::ApiUtil &self)
{
    AutoPythonAllowThreads guard;
    self.get_asynch_replies();
}

inline void get_asynch_replies2(Tango::ApiUtil &self, long timeout)
{
    AutoPythonAllowThreads guard;
    self.get_asynch_replies(timeout);
}
}; // namespace PyApiUtil

void export_api_util()
{
    bopy::class_<Tango::ApiUtil, boost::noncopyable>("ApiUtil", bopy::no_init)

        .def("instance", &Tango::ApiUtil::instance, bopy::return_value_policy<bopy::reference_existing_object>())
        .staticmethod("instance")

        .def("pending_asynch_call", &Tango::ApiUtil::pending_asynch_call)

        .def("get_asynch_replies", &PyApiUtil::get_asynch_replies1)
        .def("get_asynch_replies", &PyApiUtil::get_asynch_replies2)

        .def("set_asynch_cb_sub_model", &Tango::ApiUtil::set_asynch_cb_sub_model)
        .def("get_asynch_cb_sub_model", &Tango::ApiUtil::get_asynch_cb_sub_model)

        .def("get_env_var", &PyApiUtil::get_env_var)
        .staticmethod("get_env_var")

        .def("is_notifd_event_consumer_created", &Tango::ApiUtil::is_notifd_event_consumer_created)
        .def("is_zmq_event_consumer_created", &Tango::ApiUtil::is_zmq_event_consumer_created)
        .def("get_user_connect_timeout", &Tango::ApiUtil::get_user_connect_timeout)

        .def("in_server", (bool(Tango::ApiUtil::*)()) & Tango::ApiUtil::in_server)
        .def("get_ip_from_if", &Tango::ApiUtil::get_ip_from_if)
        .def("cleanup", &Tango::ApiUtil::cleanup)
        .staticmethod("cleanup");
}
