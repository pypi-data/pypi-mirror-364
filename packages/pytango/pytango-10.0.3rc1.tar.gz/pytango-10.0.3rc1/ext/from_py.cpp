/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "from_py.h"
#include "pyutils.h"

/// @bug Not a bug per se, but you should keep in mind: It returns a new
/// string, so if you pass it to Tango with a release flag there will be
/// no problems, but if you have to use it yourself then you must remember
/// to delete[] it!
Tango::DevString PyString_AsCorbaString(PyObject *obj_ptr)
{
    return from_str_to_char(obj_ptr);
}

void convert2array(const bopy::object &py_value, Tango::DevVarCharArray &result)
{
    PyObject *py_value_ptr = py_value.ptr();
    if(PySequence_Check(py_value_ptr) == 0)
    {
        raise_(PyExc_TypeError, param_must_be_seq);
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_value));
    result.length(size);
    if(PyBytes_Check(py_value_ptr))
    {
        char *ch = PyBytes_AS_STRING(py_value_ptr);
        for(CORBA::ULong i = 0; i < size; ++i)
        {
            result[i] = ch[i];
        }
    }
    else
    {
        for(CORBA::ULong i = 0; i < size; ++i)
        {
            unsigned char *ch = bopy::extract<unsigned char *>(py_value[i]);
            result[i] = ch[0];
        }
    }
}

void convert2array(const bopy::object &py_value, StdStringVector &result)
{
    PyObject *py_value_ptr = py_value.ptr();
    if(PySequence_Check(py_value_ptr) == 0)
    {
        raise_(PyExc_TypeError, param_must_be_seq);
    }

    if(PyBytes_Check(py_value_ptr))
    {
        result.push_back(PyBytes_AS_STRING(py_value_ptr));
    }
    else if(PyUnicode_Check(py_value_ptr))
    {
        PyObject *py_bytes_value_ptr = EncodeAsLatin1(py_value_ptr);
        result.push_back(PyBytes_AS_STRING(py_bytes_value_ptr));
        Py_DECREF(py_bytes_value_ptr);
    }
    else
    {
        size_t size = bopy::len(py_value);
        result.reserve(size);

        for(size_t i = 0; i < size; ++i)
        {
            char *vi = bopy::extract<char *>(py_value[i]);
            result.push_back(vi);
        }
    }
}

void convert2array(const bopy::object &py_value, Tango::DevVarStringArray &result)
{
    PyObject *py_value_ptr = py_value.ptr();
    if(PySequence_Check(py_value_ptr) == 0)
    {
        raise_(PyExc_TypeError, param_must_be_seq);
    }

    if(PyBytes_Check(py_value_ptr))
    {
        result.length(1);
        result[0] = CORBA::string_dup(PyBytes_AS_STRING(py_value_ptr));
    }
    else if(PyUnicode_Check(py_value_ptr))
    {
        PyObject *py_bytes_value_ptr = EncodeAsLatin1(py_value_ptr);
        result.length(1);
        result[0] = CORBA::string_dup(PyBytes_AS_STRING(py_bytes_value_ptr));
        Py_DECREF(py_bytes_value_ptr);
    }
    else
    {
        CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_value));
        result.length(size);
        for(CORBA::ULong i = 0; i < size; ++i)
        {
            result[i] = CORBA::string_dup(bopy::extract<char *>(py_value[i]));
        }
    }
}

void convert2array(const bopy::object &py_value, Tango::DevVarDoubleStringArray &result)
{
    if(!PySequence_Check(py_value.ptr()))
    {
        raise_convert2array_DevVarDoubleStringArray();
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_value));
    if(size != 2)
    {
        raise_convert2array_DevVarDoubleStringArray();
    }

    const bopy::object &py_double = py_value[0], &py_str = py_value[1];

    convert2array(py_double, result.dvalue);
    convert2array(py_str, result.svalue);
}

void convert2array(const bopy::object &py_value, Tango::DevVarLongStringArray &result)
{
    if(!PySequence_Check(py_value.ptr()))
    {
        raise_convert2array_DevVarLongStringArray();
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_value));
    if(size != 2)
    {
        raise_convert2array_DevVarLongStringArray();
    }

    const bopy::object py_long = py_value[0], py_str = py_value[1];

    convert2array(py_long, result.lvalue);
    convert2array(py_str, result.svalue);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeAlarm &attr_alarm)
{
    attr_alarm.min_alarm = from_str_to_char(py_obj.attr("min_alarm"));
    attr_alarm.max_alarm = from_str_to_char(py_obj.attr("max_alarm"));
    attr_alarm.min_warning = from_str_to_char(py_obj.attr("min_warning"));
    attr_alarm.max_warning = from_str_to_char(py_obj.attr("max_warning"));
    attr_alarm.delta_t = from_str_to_char(py_obj.attr("delta_t"));
    attr_alarm.delta_val = from_str_to_char(py_obj.attr("delta_val"));
    convert2array(py_obj.attr("extensions"), attr_alarm.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::ChangeEventProp &change_evt_prop)
{
    change_evt_prop.rel_change = from_str_to_char(py_obj.attr("rel_change"));
    change_evt_prop.abs_change = from_str_to_char(py_obj.attr("abs_change"));
    convert2array(py_obj.attr("extensions"), change_evt_prop.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::PeriodicEventProp &periodic_evt_prop)
{
    periodic_evt_prop.period = from_str_to_char(py_obj.attr("period"));
    convert2array(py_obj.attr("extensions"), periodic_evt_prop.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::ArchiveEventProp &archive_evt_prop)
{
    archive_evt_prop.rel_change = from_str_to_char(py_obj.attr("rel_change"));
    archive_evt_prop.abs_change = from_str_to_char(py_obj.attr("abs_change"));
    archive_evt_prop.period = from_str_to_char(py_obj.attr("period"));
    convert2array(py_obj.attr("extensions"), archive_evt_prop.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::EventProperties &evt_props)
{
    bopy::object py_ch_event = py_obj.attr("ch_event");
    bopy::object py_per_event = py_obj.attr("per_event");
    bopy::object py_arch_event = py_obj.attr("arch_event");

    from_py_object(py_ch_event, evt_props.ch_event);
    from_py_object(py_per_event, evt_props.per_event);
    from_py_object(py_arch_event, evt_props.arch_event);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfig &attr_conf)
{
    attr_conf.name = from_str_to_char(py_obj.attr("name"));
    attr_conf.writable = bopy::extract<Tango::AttrWriteType>(py_obj.attr("writable"));
    attr_conf.data_format = bopy::extract<Tango::AttrDataFormat>(py_obj.attr("data_format"));
    attr_conf.data_type = bopy::extract<CORBA::Long>(py_obj.attr("data_type"));
    attr_conf.max_dim_x = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_x"));
    attr_conf.max_dim_y = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_y"));
    attr_conf.description = from_str_to_char(py_obj.attr("description"));
    attr_conf.label = from_str_to_char(py_obj.attr("label"));
    attr_conf.unit = from_str_to_char(py_obj.attr("unit"));
    attr_conf.standard_unit = from_str_to_char(py_obj.attr("standard_unit"));
    attr_conf.display_unit = from_str_to_char(py_obj.attr("display_unit"));
    attr_conf.format = from_str_to_char(py_obj.attr("format"));
    attr_conf.min_value = from_str_to_char(py_obj.attr("min_value"));
    attr_conf.max_value = from_str_to_char(py_obj.attr("max_value"));
    attr_conf.min_alarm = from_str_to_char(py_obj.attr("min_alarm"));
    attr_conf.max_alarm = from_str_to_char(py_obj.attr("max_alarm"));
    attr_conf.writable_attr_name = from_str_to_char(py_obj.attr("writable_attr_name"));
    convert2array(py_obj.attr("extensions"), attr_conf.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfig_2 &attr_conf)
{
    attr_conf.name = from_str_to_char(py_obj.attr("name"));
    attr_conf.writable = bopy::extract<Tango::AttrWriteType>(py_obj.attr("writable"));
    attr_conf.data_format = bopy::extract<Tango::AttrDataFormat>(py_obj.attr("data_format"));
    attr_conf.data_type = bopy::extract<CORBA::Long>(py_obj.attr("data_type"));
    attr_conf.max_dim_x = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_x"));
    attr_conf.max_dim_y = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_y"));
    attr_conf.description = from_str_to_char(py_obj.attr("description"));
    attr_conf.label = from_str_to_char(py_obj.attr("label"));
    attr_conf.unit = from_str_to_char(py_obj.attr("unit"));
    attr_conf.standard_unit = from_str_to_char(py_obj.attr("standard_unit"));
    attr_conf.display_unit = from_str_to_char(py_obj.attr("display_unit"));
    attr_conf.format = from_str_to_char(py_obj.attr("format"));
    attr_conf.min_value = from_str_to_char(py_obj.attr("min_value"));
    attr_conf.max_value = from_str_to_char(py_obj.attr("max_value"));
    attr_conf.min_alarm = from_str_to_char(py_obj.attr("min_alarm"));
    attr_conf.max_alarm = from_str_to_char(py_obj.attr("max_alarm"));
    attr_conf.writable_attr_name = from_str_to_char(py_obj.attr("writable_attr_name"));
    attr_conf.level = bopy::extract<Tango::DispLevel>(py_obj.attr("level"));
    convert2array(py_obj.attr("extensions"), attr_conf.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfig_3 &attr_conf)
{
    attr_conf.name = from_str_to_char(py_obj.attr("name"));
    attr_conf.writable = bopy::extract<Tango::AttrWriteType>(py_obj.attr("writable"));
    attr_conf.data_format = bopy::extract<Tango::AttrDataFormat>(py_obj.attr("data_format"));
    attr_conf.data_type = bopy::extract<CORBA::Long>(py_obj.attr("data_type"));
    attr_conf.max_dim_x = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_x"));
    attr_conf.max_dim_y = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_y"));
    attr_conf.description = from_str_to_char(py_obj.attr("description"));
    attr_conf.label = from_str_to_char(py_obj.attr("label"));
    attr_conf.unit = from_str_to_char(py_obj.attr("unit"));
    attr_conf.standard_unit = from_str_to_char(py_obj.attr("standard_unit"));
    attr_conf.display_unit = from_str_to_char(py_obj.attr("display_unit"));
    attr_conf.format = from_str_to_char(py_obj.attr("format"));
    attr_conf.min_value = from_str_to_char(py_obj.attr("min_value"));
    attr_conf.max_value = from_str_to_char(py_obj.attr("max_value"));
    attr_conf.writable_attr_name = from_str_to_char(py_obj.attr("writable_attr_name"));
    attr_conf.level = bopy::extract<Tango::DispLevel>(py_obj.attr("level"));

    bopy::object py_att_alarm = py_obj.attr("att_alarm");
    bopy::object py_event_prop = py_obj.attr("event_prop");

    from_py_object(py_att_alarm, attr_conf.att_alarm);
    from_py_object(py_event_prop, attr_conf.event_prop);
    convert2array(py_obj.attr("extensions"), attr_conf.extensions);
    convert2array(py_obj.attr("sys_extensions"), attr_conf.sys_extensions);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfig_5 &attr_conf)
{
    attr_conf.name = from_str_to_char(py_obj.attr("name"));
    attr_conf.writable = bopy::extract<Tango::AttrWriteType>(py_obj.attr("writable"));
    attr_conf.data_format = bopy::extract<Tango::AttrDataFormat>(py_obj.attr("data_format"));
    attr_conf.data_type = bopy::extract<CORBA::Long>(py_obj.attr("data_type"));
    attr_conf.memorized = bopy::extract<CORBA::Boolean>(py_obj.attr("memorized"));
    attr_conf.mem_init = bopy::extract<CORBA::Boolean>(py_obj.attr("mem_init"));
    attr_conf.max_dim_x = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_x"));
    attr_conf.max_dim_y = bopy::extract<CORBA::Long>(py_obj.attr("max_dim_y"));
    attr_conf.description = from_str_to_char(py_obj.attr("description"));
    attr_conf.label = from_str_to_char(py_obj.attr("label"));
    attr_conf.unit = from_str_to_char(py_obj.attr("unit"));
    attr_conf.standard_unit = from_str_to_char(py_obj.attr("standard_unit"));
    attr_conf.display_unit = from_str_to_char(py_obj.attr("display_unit"));
    attr_conf.format = from_str_to_char(py_obj.attr("format"));
    attr_conf.min_value = from_str_to_char(py_obj.attr("min_value"));
    attr_conf.max_value = from_str_to_char(py_obj.attr("max_value"));
    attr_conf.writable_attr_name = from_str_to_char(py_obj.attr("writable_attr_name"));
    attr_conf.level = bopy::extract<Tango::DispLevel>(py_obj.attr("level"));
    attr_conf.root_attr_name = from_str_to_char(py_obj.attr("root_attr_name"));

    convert2array(py_obj.attr("enum_labels"), attr_conf.enum_labels);

    bopy::object py_att_alarm = py_obj.attr("att_alarm");
    bopy::object py_event_prop = py_obj.attr("event_prop");

    from_py_object(py_att_alarm, attr_conf.att_alarm);
    from_py_object(py_event_prop, attr_conf.event_prop);
    convert2array(py_obj.attr("extensions"), attr_conf.extensions);
    convert2array(py_obj.attr("sys_extensions"), attr_conf.sys_extensions);
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfigList &attr_conf_list)
{
    PyObject *py_obj_ptr = py_obj.ptr();

    if(!PySequence_Check(py_obj_ptr))
    {
        attr_conf_list.length(1);
        from_py_object(py_obj, attr_conf_list[0]);
        return;
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_obj));
    attr_conf_list.length(size);
    for(CORBA::ULong i = 0; i < size; ++i)
    {
        bopy::object tmp = py_obj[i];
        from_py_object(tmp, attr_conf_list[i]);
    }
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfigList_2 &attr_conf_list)
{
    PyObject *py_obj_ptr = py_obj.ptr();

    if(!PySequence_Check(py_obj_ptr))
    {
        attr_conf_list.length(1);
        from_py_object(py_obj, attr_conf_list[0]);
        return;
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_obj));
    attr_conf_list.length(size);
    for(CORBA::ULong i = 0; i < size; ++i)
    {
        bopy::object tmp = py_obj[i];
        from_py_object(tmp, attr_conf_list[i]);
    }
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfigList_3 &attr_conf_list)
{
    PyObject *py_obj_ptr = py_obj.ptr();

    if(!PySequence_Check(py_obj_ptr))
    {
        attr_conf_list.length(1);
        from_py_object(py_obj, attr_conf_list[0]);
        return;
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_obj));
    attr_conf_list.length(size);
    for(CORBA::ULong i = 0; i < size; ++i)
    {
        bopy::object tmp = py_obj[i];
        from_py_object(tmp, attr_conf_list[i]);
    }
}

void from_py_object(bopy::object &py_obj, Tango::AttributeConfigList_5 &attr_conf_list)
{
    PyObject *py_obj_ptr = py_obj.ptr();

    if(!PySequence_Check(py_obj_ptr))
    {
        attr_conf_list.length(1);
        from_py_object(py_obj, attr_conf_list[0]);
        return;
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_obj));
    attr_conf_list.length(size);
    for(CORBA::ULong i = 0; i < size; ++i)
    {
        bopy::object tmp = py_obj[i];
        from_py_object(tmp, attr_conf_list[i]);
    }
}

void from_py_object(bopy::object &py_obj, Tango::PipeConfig &pipe_conf)
{
    pipe_conf.name = from_str_to_char(py_obj.attr("name"));
    pipe_conf.description = from_str_to_char(py_obj.attr("description"));
    pipe_conf.label = from_str_to_char(py_obj.attr("label"));
    pipe_conf.level = bopy::extract<Tango::DispLevel>(py_obj.attr("level"));
    pipe_conf.writable = bopy::extract<Tango::PipeWriteType>(py_obj.attr("writable"));
    convert2array(py_obj.attr("extensions"), pipe_conf.extensions);
}

void from_py_object(bopy::object &py_obj, Tango::PipeConfigList &pipe_conf_list)
{
    PyObject *py_obj_ptr = py_obj.ptr();

    if(!PySequence_Check(py_obj_ptr))
    {
        pipe_conf_list.length(1);
        from_py_object(py_obj, pipe_conf_list[0]);
        return;
    }

    CORBA::ULong size = static_cast<CORBA::ULong>(bopy::len(py_obj));
    pipe_conf_list.length(size);
    for(CORBA::ULong i = 0; i < size; ++i)
    {
        bopy::object tmp = py_obj[i];
        from_py_object(tmp, pipe_conf_list[i]);
    }
}
