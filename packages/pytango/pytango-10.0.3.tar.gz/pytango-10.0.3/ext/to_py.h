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

struct DevEncoded_to_tuple
{
    static inline PyObject *convert(Tango::DevEncoded const &a)
    {
        bopy::str encoded_format(a.encoded_format);
        bopy::object encoded_data = bopy::object(bopy::handle<>(PyBytes_FromStringAndSize(
            (const char *) a.encoded_data.get_buffer(), (Py_ssize_t) a.encoded_data.length())));
        bopy::object result = bopy::make_tuple(encoded_format, encoded_data);
        return bopy::incref(result.ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <typename ContainerType>
struct to_list
{
    static inline PyObject *convert(ContainerType const &a)
    {
        bopy::list result;
        typedef typename ContainerType::const_iterator const_iter;
        for(const_iter it = a.begin(); it != a.end(); it++)
        {
            result.append(bopy::object(*it));
        }
        return bopy::incref(result.ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyList_Type;
    }
};

template <typename ContainerType>
struct to_tuple
{
    static inline PyObject *convert(ContainerType const &a)
    {
        typedef typename ContainerType::const_iterator const_iter;
        PyObject *t = PyTuple_New(a.size());
        int32_t i = 0;
        for(const_iter it = a.begin(); it != a.end(); ++it, ++i)
        {
            PyTuple_SetItem(t, i, bopy::incref(it->ptr()));
        }
        return t;
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <typename CorbaContainerType>
struct CORBA_sequence_to_tuple
{
    static PyObject *convert(CorbaContainerType const &a)
    {
        Py_ssize_t size = a.length();
        PyObject *t = PyTuple_New(size);
        for(Py_ssize_t i = 0; i < size; ++i)
        {
            bopy::object x(a[i]);
            PyTuple_SetItem(t, i, bopy::incref(x.ptr()));
        }
        return t;
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <>
struct CORBA_sequence_to_tuple<Tango::DevVarStringArray>
{
    static PyObject *convert(Tango::DevVarStringArray const &a)
    {
        Py_ssize_t size = a.length();
        PyObject *t = PyTuple_New(size);
        for(Py_ssize_t i = 0; i < size; ++i)
        {
            bopy::object x = from_char_to_boost_str(a[i].in());
            PyTuple_SetItem(t, i, bopy::incref(x.ptr()));
        }
        return t;
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <>
struct CORBA_sequence_to_tuple<Tango::DevVarLongStringArray>
{
    static PyObject *convert(Tango::DevVarLongStringArray const &a)
    {
        Py_ssize_t lsize = a.lvalue.length();
        Py_ssize_t ssize = a.svalue.length();
        PyObject *lt = PyTuple_New(lsize);
        PyObject *st = PyTuple_New(ssize);

        for(Py_ssize_t i = 0; i < lsize; ++i)
        {
            bopy::object x(a.lvalue[i]);
            PyTuple_SetItem(lt, i, bopy::incref(x.ptr()));
        }

        for(Py_ssize_t i = 0; i < ssize; ++i)
        {
            bopy::object x = from_char_to_boost_str(a.svalue[i].in());
            PyTuple_SetItem(st, i, bopy::incref(x.ptr()));
        }
        PyObject *t = PyTuple_New(2);
        PyTuple_SetItem(t, 0, lt);
        PyTuple_SetItem(t, 1, st);
        return t;
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <>
struct CORBA_sequence_to_tuple<Tango::DevVarDoubleStringArray>
{
    static PyObject *convert(Tango::DevVarDoubleStringArray const &a)
    {
        Py_ssize_t dsize = a.dvalue.length();
        Py_ssize_t ssize = a.svalue.length();
        PyObject *dt = PyTuple_New(dsize);
        PyObject *st = PyTuple_New(ssize);

        for(Py_ssize_t i = 0; i < dsize; ++i)
        {
            bopy::object x(a.dvalue[i]);
            PyTuple_SetItem(dt, i, bopy::incref(x.ptr()));
        }

        for(Py_ssize_t i = 0; i < ssize; ++i)
        {
            bopy::object x = from_char_to_boost_str(a.svalue[i].in());
            PyTuple_SetItem(st, i, bopy::incref(x.ptr()));
        }
        PyObject *t = PyTuple_New(2);
        PyTuple_SetItem(t, 0, dt);
        PyTuple_SetItem(t, 1, st);
        return t;
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyTuple_Type;
    }
};

template <typename CorbaContainerType>
struct CORBA_sequence_to_list
{
    static PyObject *convert(CorbaContainerType const &a)
    {
        Py_ssize_t size = a.length();
        bopy::list ret;
        for(Py_ssize_t i = 0; i < size; ++i)
        {
            ret.append(a[i]);
        }
        return bopy::incref(ret.ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyList_Type;
    }
};

template <>
struct CORBA_sequence_to_list<Tango::DevVarStringArray>
{
    static bopy::list to_list(Tango::DevVarStringArray const &a)
    {
        Py_ssize_t size = a.length();
        bopy::list ret;
        for(Py_ssize_t i = 0; i < size; ++i)
        {
            bopy::object x = from_char_to_boost_str(a[i].in());
            ret.append(x);
        }
        return ret;
    }

    static PyObject *convert(Tango::DevVarStringArray const &a)
    {
        return bopy::incref(to_list(a).ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyList_Type;
    }
};

template <>
struct CORBA_sequence_to_list<Tango::DevVarLongStringArray>
{
    static PyObject *convert(Tango::DevVarLongStringArray const &a)
    {
        Py_ssize_t lsize = a.lvalue.length();
        Py_ssize_t ssize = a.svalue.length();

        bopy::list ret, lt, st;
        for(Py_ssize_t i = 0; i < lsize; ++i)
        {
            lt.append(a.lvalue[i]);
        }

        for(Py_ssize_t i = 0; i < ssize; ++i)
        {
            bopy::object x = from_char_to_boost_str(a.svalue[i].in());
            st.append(x);
        }

        ret.append(lt);
        ret.append(st);

        return bopy::incref(ret.ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyList_Type;
    }
};

template <>
struct CORBA_sequence_to_list<Tango::DevVarDoubleStringArray>
{
    static PyObject *convert(Tango::DevVarDoubleStringArray const &a)
    {
        Py_ssize_t dsize = a.dvalue.length();
        Py_ssize_t ssize = a.svalue.length();

        bopy::list ret, dt, st;
        for(Py_ssize_t i = 0; i < dsize; ++i)
        {
            dt.append(a.dvalue[i]);
        }

        for(Py_ssize_t i = 0; i < ssize; ++i)
        {
            bopy::object x = from_char_to_boost_str(a.svalue[i].in());
            st.append(x);
        }

        ret.append(dt);
        ret.append(st);

        return bopy::incref(ret.ptr());
    }

    static const PyTypeObject *get_pytype()
    {
        return &PyList_Type;
    }
};

struct CORBA_String_member_to_str
{
    static inline PyObject *convert(CORBA::String_member const &cstr)
    {
        return from_char_to_python_str(cstr.in());
    }

    // static const PyTypeObject* get_pytype() { return &PyBytes_Type; }
};

struct CORBA_String_member_to_str2
{
    static inline PyObject *convert(_CORBA_String_member const &cstr)
    {
        return from_char_to_python_str(cstr.in());
    }

    // static const PyTypeObject* get_pytype() { return &PyBytes_Type; }
};

struct CORBA_String_element_to_str
{
    static inline PyObject *convert(_CORBA_String_element const &cstr)
    {
        return from_char_to_python_str(cstr.in());
    }

    // static const PyTypeObject* get_pytype() { return &PyBytes_Type; }
};

struct String_to_str
{
    static inline PyObject *convert(std::string const &cstr)
    {
        return from_char_to_python_str(cstr);
    }

    // static const PyTypeObject* get_pytype() { return &PyBytes_Type; }
};

struct char_ptr_to_str
{
    static inline PyObject *convert(const char *cstr)
    {
        return from_char_to_python_str(cstr);
    }

    // static const PyTypeObject* get_pytype() { return &PyBytes_Type; }
};

bopy::object to_py(const Tango::AttributeAlarm &);
bopy::object to_py(const Tango::ChangeEventProp &);
bopy::object to_py(const Tango::PeriodicEventProp &);
bopy::object to_py(const Tango::ArchiveEventProp &);
bopy::object to_py(const Tango::EventProperties &);

template <typename T>
void to_py(Tango::MultiAttrProp<T> &multi_attr_prop, bopy::object &py_multi_attr_prop)
{
    if(py_multi_attr_prop.ptr() == Py_None)
    {
        PYTANGO_MOD
        py_multi_attr_prop = pytango.attr("MultiAttrProp")();
    }

    py_multi_attr_prop.attr("label") = multi_attr_prop.label;
    py_multi_attr_prop.attr("description") = multi_attr_prop.description;
    py_multi_attr_prop.attr("unit") = multi_attr_prop.unit;
    py_multi_attr_prop.attr("standard_unit") = multi_attr_prop.standard_unit;
    py_multi_attr_prop.attr("display_unit") = multi_attr_prop.display_unit;
    py_multi_attr_prop.attr("format") = multi_attr_prop.format;
    py_multi_attr_prop.attr("min_value") = multi_attr_prop.min_value.get_str();
    py_multi_attr_prop.attr("max_value") = multi_attr_prop.max_value.get_str();
    py_multi_attr_prop.attr("min_alarm") = multi_attr_prop.min_alarm.get_str();
    py_multi_attr_prop.attr("max_alarm") = multi_attr_prop.max_alarm.get_str();
    py_multi_attr_prop.attr("min_warning") = multi_attr_prop.min_warning.get_str();
    py_multi_attr_prop.attr("max_warning") = multi_attr_prop.max_warning.get_str();
    py_multi_attr_prop.attr("delta_t") = multi_attr_prop.delta_t.get_str();
    py_multi_attr_prop.attr("delta_val") = multi_attr_prop.delta_val.get_str();
    py_multi_attr_prop.attr("event_period") = multi_attr_prop.event_period.get_str();
    py_multi_attr_prop.attr("archive_period") = multi_attr_prop.archive_period.get_str();
    py_multi_attr_prop.attr("rel_change") = multi_attr_prop.rel_change.get_str();
    py_multi_attr_prop.attr("abs_change") = multi_attr_prop.abs_change.get_str();
    py_multi_attr_prop.attr("archive_rel_change") = multi_attr_prop.archive_rel_change.get_str();
    py_multi_attr_prop.attr("archive_abs_change") = multi_attr_prop.archive_abs_change.get_str();
}

bopy::object to_py(const Tango::AttributeConfig &, bopy::object py_attr_conf);
bopy::object to_py(const Tango::AttributeConfig_2 &, bopy::object py_attr_conf);
bopy::object to_py(const Tango::AttributeConfig_3 &, bopy::object py_attr_conf);
bopy::object to_py(const Tango::AttributeConfig_5 &, bopy::object py_attr_conf);

bopy::list to_py(const Tango::AttributeConfigList &);
bopy::list to_py(const Tango::AttributeConfigList_2 &);
bopy::list to_py(const Tango::AttributeConfigList_3 &);
bopy::list to_py(const Tango::AttributeConfigList_5 &);

bopy::object to_py(const Tango::PipeConfig &, bopy::object);

bopy::object to_py(const Tango::PipeConfigList &, bopy::object);

template <class T>
inline bopy::object to_py_list(const T *seq)
{
    return bopy::object(bopy::handle<>(CORBA_sequence_to_list<T>::convert(*seq)));
}

template <class T>
inline bopy::object to_py_tuple(const T *seq)
{
    return bopy::object(bopy::handle<>(CORBA_sequence_to_tuple<T>::convert(*seq)));
}
