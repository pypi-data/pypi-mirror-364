/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "pytgutils.h"
#include "device_attribute.h"

void export_group_reply_list();
void export_group_reply();

namespace PyGroup
{
// Implementation taken from Scott Meyers "Effective C++"
// with minor C++11 cleanups
template <class T>
class auto_ptr
{
  public:
    explicit auto_ptr(T *p = nullptr) :
        pointee(p)
    {
    }

    template <class U>
    auto_ptr(auto_ptr<U> &rhs) :
        pointee(rhs.release())
    {
    }

    ~auto_ptr()
    {
        if(pointee != nullptr)
        {
            AutoPythonAllowThreads guard;
            delete pointee;
        }
    }

    template <class U>
    auto_ptr<T> &operator=(auto_ptr<U> &rhs)
    {
        if(this != &rhs)
        {
            reset(rhs.release());
        }
        return *this;
    }

    T &operator*() const
    {
        return *pointee;
    }

    T *operator->() const
    {
        return pointee;
    }

    T *get() const
    {
        return pointee;
    }

    T *release()
    {
        T *oldPointee = pointee;
        pointee = nullptr;
        return oldPointee;
    }

    void reset(T *p = nullptr)
    {
        if(pointee != p)
        {
            if(pointee != nullptr)
            {
                AutoPythonAllowThreads guard;
                delete pointee;
            }
            pointee = p;
        }
    }

  private:
    T *pointee;
};

// Taken from https://stackoverflow.com/a/14786216
template <typename T>
T *get_pointer(PyGroup::auto_ptr<T> const &p)
{
    // notice the const_cast<> at this point
    // for some unknown reason, bp likes to have it like that
    return const_cast<T *>(p.get());
}
} // namespace PyGroup

// Taken from
// https://www.boost.org/doc/libs/1_84_0/libs/python/doc/html/reference/utility_and_infrastructure/boost_python_pointee_hpp.html
namespace boost
{
namespace python
{
template <class T>
struct pointee<PyGroup::auto_ptr<T>>
{
    typedef T type;
};
} // namespace python
} // namespace boost

namespace PyGroup
{

void add(Tango::Group &self, PyGroup::auto_ptr<Tango::Group> grp, int timeout_ms)
{
    Tango::Group *grp_ptr = grp.get();

    if(grp_ptr)
    {
        // After adding grp_ptr into self, self is the responsible of
        // deleting grp_ptr, so we "nullify" the grp object. It's python
        // counterpart will still be available, but any method call will
        // return an exception.
        self.add(grp_ptr, timeout_ms);
        grp.release();
    }
    else
    {
        raise_(PyExc_TypeError,
               "Param \"group\" is null. It probably means that it has"
               " already been inserted in another group.");
    }
}

Tango::GroupCmdReplyList command_inout_reply(Tango::Group &self, long req_id, long timeout_ms)
{
    AutoPythonAllowThreads guard;
    return self.command_inout_reply(req_id, timeout_ms);
}

static void __update_data_format(Tango::Group &self, Tango::GroupAttrReplyList &r)
{
    // Usually we pass a device_proxy to "convert_to_python" in order to
    // get the data_format of the DeviceAttribute for Tango versions
    // older than 7.0. However, GroupAttrReply has no device_proxy to use!
    // So, we are using update_data_format() in here.
    // The conver_to_python method is called, without the usual
    // device_proxy argument, in PyGroupAttrReply::get_data().
    Tango::GroupAttrReplyList::iterator i, e = r.end();
    for(i = r.begin(); i != e; ++i)
    {
        Tango::DeviceProxy *dev_proxy = self.get_device(i->dev_name());
        if(!dev_proxy)
        {
            continue;
        }
        PyDeviceAttribute::update_data_format(*dev_proxy, &(i->get_data()), 1);
    }
}

Tango::GroupAttrReplyList read_attribute_reply(Tango::Group &self, long req_id, long timeout_ms = 0)
{
    Tango::GroupAttrReplyList r;
    {
        AutoPythonAllowThreads guard;
        r = self.read_attribute_reply(req_id, timeout_ms);
    }
    __update_data_format(self, r);
    return r;
}

Tango::GroupAttrReplyList read_attributes_reply(Tango::Group &self, long req_id, long timeout_ms = 0)
{
    Tango::GroupAttrReplyList r;
    {
        AutoPythonAllowThreads guard;
        r = self.read_attributes_reply(req_id, timeout_ms);
    }
    __update_data_format(self, r);
    return r;
}

long read_attributes_asynch(Tango::Group &self, bopy::object py_value, bool forward = true)
{
    StdStringVector r;
    convert2array(py_value, r);
    return self.read_attributes_asynch(r, forward);
}

long write_attribute_asynch(
    Tango::Group &self, const std::string &attr_name, bopy::object py_value, bool forward = true, bool multi = false)
{
    Tango::DeviceProxy *dev_proxy = self.get_device(1);
    // If !dev_proxy (no device added in self or his children) then we
    // don't initialize dev_attr. As a result, the reply will be empty.
    /// @todo or should we raise an exception instead?
    if(!dev_proxy)
    {
        Tango::DeviceAttribute dev_attr;
        dev_attr.set_name(attr_name.c_str());
        AutoPythonAllowThreads guard;
        return self.write_attribute_asynch(dev_attr, forward);
    }

    // Try to see if we can get attribute information from any device in
    // the group
    Tango::AttributeInfoEx attr_info;
    bool has_attr_info = false;
    {
        AutoPythonAllowThreads guard;
        for(long dev_idx = 1; dev_idx <= self.get_size(); ++dev_idx)
        {
            try
            {
                attr_info = self[dev_idx]->get_attribute_config(attr_name);
                has_attr_info = true;
                break;
            }
            catch(...)
            {
            }
        }
    }

    if(multi)
    {
        if(!PySequence_Check(py_value.ptr()))
        {
            raise_(PyExc_TypeError,
                   "When multi is set, value must be a python sequence "
                   "(ex: list or tuple)");
        }

        Py_ssize_t attr_nb = bopy::len(py_value);
        std::vector<Tango::DeviceAttribute> dev_attr(attr_nb);

        if(has_attr_info)
        {
            for(Py_ssize_t i = 0; i < attr_nb; ++i)
            {
                PyDeviceAttribute::reset(dev_attr[i], attr_info, py_value[i]);
            }
        }
        else
        {
            for(Py_ssize_t i = 0; i < attr_nb; ++i)
            {
                dev_attr[i].set_name(attr_name.c_str());
            }
        }
        AutoPythonAllowThreads guard;
        return self.write_attribute_asynch(dev_attr, forward);
    }
    else
    {
        Tango::DeviceAttribute dev_attr;
        if(has_attr_info)
        {
            PyDeviceAttribute::reset(dev_attr, attr_info, py_value);
        }
        else
        {
            dev_attr.set_name(attr_name.c_str());
        }
        // If !dev_proxy (no device added in self or his children) then we
        // don't initialize dev_attr. As a result, the reply will be empty.
        /// @todo or should we raise an exception instead?

        AutoPythonAllowThreads guard;
        return self.write_attribute_asynch(dev_attr, forward);
    }
}

Tango::GroupReplyList write_attribute_reply(Tango::Group &self, long req_id, long timeout_ms = 0)
{
    AutoPythonAllowThreads guard;
    return self.write_attribute_reply(req_id, timeout_ms);
}
} // namespace PyGroup

void export_group()
{
    export_group_reply();
    export_group_reply_list();
    //    export_group_element();

    //    class_<Tango::Group, bases<Tango::GroupElement>,
    //           unique_pointer<Tango::Group>, boost::noncopyable > Group(
    //        "__Group",
    //        init<const std::string&>())
    //    ;
    bopy::class_<Tango::Group, PyGroup::auto_ptr<Tango::Group>, boost::noncopyable> Group(
        "__Group", bopy::init<const std::string &>());

    Group
        .def("_add",
             (void(Tango::Group::*)(const std::string &, int)) & Tango::Group::add,
             (arg_("self"), arg_("pattern"), arg_("timeout_ms") = -1))
        .def("_add",
             (void(Tango::Group::*)(const std::vector<std::string> &, int)) & Tango::Group::add,
             (arg_("self"), arg_("patterns"), arg_("timeout_ms") = -1))
        .def("_add", PyGroup::add, (arg_("self"), arg_("group"), arg_("timeout_ms") = -1))

        .def("_remove",
             (void(Tango::Group::*)(const std::string &, bool)) & Tango::Group::remove,
             (arg_("self"), arg_("pattern"), arg_("forward") = true))
        .def("_remove",
             (void(Tango::Group::*)(const std::vector<std::string> &, bool)) & Tango::Group::remove,
             (arg_("self"), arg_("patterns"), arg_("forward") = true))
        .def("get_group",
             &Tango::Group::get_group,
             (arg_("self"), arg_("group_name")),
             bopy::return_internal_reference<1>())
        .def("get_size", &Tango::Group::get_size, (arg_("self"), arg_("forward") = true))

        .def("remove_all", &Tango::Group::remove_all)

        // GroupElement redefinitions of enable/disable. If I didn't
        // redefine them, the later Group only definitions would
        // hide the ones defined in GroupElement.
        .def("enable", &Tango::GroupElement::enable, (arg_("self")))
        .def("disable", &Tango::GroupElement::disable, (arg_("self")))
        .def("enable", &Tango::Group::enable, (arg_("self"), arg_("dev_name"), arg_("forward") = true))
        .def("disable", &Tango::Group::disable, (arg_("self"), arg_("dev_name"), arg_("forward") = true))

        .def("get_device_list", &Tango::Group::get_device_list, (arg_("self"), arg_("forward") = true))

        .def("command_inout_asynch",
             (long(Tango::Group::*)(const std::string &, bool, bool)) & Tango::Group::command_inout_asynch,
             (arg_("self"), arg_("cmd_name"), arg_("forget") = false, arg_("forward") = true))
        .def("command_inout_asynch",
             (long(Tango::Group::*)(const std::string &, const Tango::DeviceData &, bool, bool)) &
                 Tango::Group::command_inout_asynch,
             (arg_("self"), arg_("cmd_name"), arg_("param"), arg_("forget") = false, arg_("forward") = true))
        .def("command_inout_asynch",
             (long(Tango::Group::*)(const std::string &, const std::vector<Tango::DeviceData> &, bool, bool)) &
                 Tango::Group::command_inout_asynch,
             (arg_("self"), arg_("cmd_name"), arg_("param"), arg_("forget") = false, arg_("forward") = true))
        .def(
            "command_inout_reply", PyGroup::command_inout_reply, (arg_("self"), arg_("req_id"), arg_("timeout_ms") = 0))
        .def("read_attribute_asynch",
             &Tango::Group::read_attribute_asynch,
             (arg_("self"), arg_("attr_name"), arg_("forward") = true))
        .def("read_attribute_reply",
             PyGroup::read_attribute_reply,
             (arg_("self"), arg_("req_id"), arg_("timeout_ms") = 0))
        .def("read_attributes_asynch",
             PyGroup::read_attributes_asynch,
             (arg_("self"), arg_("attr_names"), arg_("forward") = true))
        .def("read_attributes_reply",
             PyGroup::read_attributes_reply,
             (arg_("self"), arg_("req_id"), arg_("timeout_ms") = 0))
        .def("write_attribute_asynch",
             PyGroup::write_attribute_asynch,
             (arg_("self"), arg_("attr_name"), arg_("value"), arg_("forward") = true, arg_("multi") = false))
        .def("write_attribute_reply",
             PyGroup::write_attribute_reply,
             (arg_("self"), arg_("req_id"), arg_("timeout_ms") = 0))

        .def("get_parent", &Tango::Group::get_parent, (arg_("self")), bopy::return_internal_reference<1>())
        .def("contains", &Tango::Group::contains, (arg_("self"), arg_("pattern"), arg_("forward") = true))
        .def("get_device",
             (Tango::DeviceProxy * (Tango::Group::*) (const std::string &) ) & Tango::Group::get_device,
             (arg_("self"), arg_("dev_name")),
             bopy::return_internal_reference<1>())
        .def("get_device",
             (Tango::DeviceProxy * (Tango::Group::*) (long) ) & Tango::Group::get_device,
             (arg_("self"), arg_("idx")),
             bopy::return_internal_reference<1>())
        .def("ping", &Tango::Group::ping, (arg_("self"), arg_("forward") = true))
        .def("set_timeout_millis", &Tango::Group::set_timeout_millis, (arg_("self"), arg_("timeout_ms")))
        .def("get_name",
             &Tango::Group::get_name,
             (arg_("self")),
             bopy::return_value_policy<bopy::copy_const_reference>())
        .def("get_fully_qualified_name", &Tango::Group::get_fully_qualified_name, (arg_("self")))
        .def("enable", &Tango::Group::enable, (arg_("self")))
        .def("disable", &Tango::Group::disable, (arg_("self")))
        .def("is_enabled", &Tango::Group::is_enabled, (arg_("self")))
        .def("name_equals", &Tango::Group::name_equals, (arg_("self")))
        .def("name_matches", &Tango::Group::name_matches, (arg_("self")))

        ;

    // I am not exporting "find", so all the GroupElemens will be
    // Groups (there's no way to access a GroupDeviceElement)
    //     class_<Tango::GroupDeviceElement, bases<Tango::GroupElement>, boost::noncopyable > GroupDeviceElement(
    //         "GroupDeviceElement",
    //         no_init)
    //     ;
}
