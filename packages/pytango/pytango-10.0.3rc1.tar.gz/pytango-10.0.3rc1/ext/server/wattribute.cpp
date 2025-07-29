/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"
#include "fast_from_py.h"

/**
 * Helper method to Limit the max number of element to send to C++
 *
 * @param[in,out] len the length. if x*y is lower the len, the len is updated to x*y
 * @param[in] x the x dimension
 * @param[in] y the y dimension
 */
static inline void twod2oned(long &len, long x, long y)
{
    if(y <= 0)
    {
        if(x < len)
        {
            len = x;
        }
    }
    else
    {
        long max_elt = x * y;
        if(max_elt < len)
        {
            len = max_elt;
        }
    }
}

inline static void throw_wrong_python_data_type(const std::string &att_name, const char *method)
{
    TangoSys_OMemStream o;
    o << "Wrong Python type for attribute " << att_name << std::ends;
    Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), method);
}

namespace PyWAttribute
{
/// @name Min/Max value
/// @{
template <long tangoTypeConst>
PyObject *__get_min_value(Tango::WAttribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_min_value(tg_val);
    bopy::object py_value(tg_val);

    return bopy::incref(py_value.ptr());
}

PyObject *get_min_value(Tango::WAttribute &att)
{
    long type = att.get_data_type();

    if(type == Tango::DEV_ENCODED)
    {
        type = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, return __get_min_value, att);
    return 0;
}

template <long tangoTypeConst>
PyObject *__get_max_value(Tango::WAttribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_max_value(tg_val);
    bopy::object py_value(tg_val);
    return bopy::incref(py_value.ptr());
}

PyObject *get_max_value(Tango::WAttribute &att)
{
    long type = att.get_data_type();

    if(type == Tango::DEV_ENCODED)
    {
        type = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, return __get_max_value, att);
    return 0;
}

template <long tangoTypeConst>
inline void _set_min_value(Tango::WAttribute &self, bopy::object value)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_min_value(c_value);
}

inline void set_min_value(Tango::WAttribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_min_value(value_convert());
    }
    else
    {
        long tangoTypeConst = self.get_data_type();
        // TODO: the below line is a neat trick to properly raise a Tango exception if a property is set
        // for one of the forbidden attribute data types; code dependent on Tango C++ implementation
        if(tangoTypeConst == Tango::DEV_STRING || tangoTypeConst == Tango::DEV_BOOLEAN ||
           tangoTypeConst == Tango::DEV_STATE)
        {
            tangoTypeConst = Tango::DEV_DOUBLE;
        }
        else if(tangoTypeConst == Tango::DEV_ENCODED)
        {
            tangoTypeConst = Tango::DEV_UCHAR;
        }

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, _set_min_value, self, value);
    }
}

template <long tangoTypeConst>
inline void _set_max_value(Tango::WAttribute &self, bopy::object value)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_max_value(c_value);
}

inline void set_max_value(Tango::WAttribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_max_value(value_convert());
    }
    else
    {
        long tangoTypeConst = self.get_data_type();
        // TODO: the below line is a neat trick to properly raise a Tango exception if a property is set
        // for one of the forbidden attribute data types; code dependent on Tango C++ implementation
        if(tangoTypeConst == Tango::DEV_STRING || tangoTypeConst == Tango::DEV_BOOLEAN ||
           tangoTypeConst == Tango::DEV_STATE)
        {
            tangoTypeConst = Tango::DEV_DOUBLE;
        }
        else if(tangoTypeConst == Tango::DEV_ENCODED)
        {
            tangoTypeConst = Tango::DEV_UCHAR;
        }

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, _set_max_value, self, value);
    }
}

/// @}

/// @name set_write_value
/// @{

template <long tangoTypeConst>
inline void __set_write_value_scalar(Tango::WAttribute &att, bopy::object &value)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    /*extract<TangoScalarType> val(value.ptr());
    if (!val.check())
    {
        throw_wrong_python_data_type(att.get_name(), "set_write_value()");
    }
    TangoScalarType cpp_value = val;
    */
    TangoScalarType cpp_value;
    from_py<tangoTypeConst>::convert(value.ptr(), cpp_value);
    att.set_write_value(cpp_value);
}

template <>
inline void __set_write_value_scalar<Tango::DEV_ENCODED>(Tango::WAttribute &att, bopy::object &value)
{
    Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute",
                                   "set_write_value is not supported for DEV_ENCODED attributes.",
                                   "set_write_value()");
}

inline void __check_array_length(PyObject *seq_ptr, long &x_dim, long &y_dim, const std::string &att_name)
{
    long len = static_cast<long>(PySequence_Size(seq_ptr));

    PyObject *first_element = PySequence_GetItem(seq_ptr, 0);

    TangoSys_OMemStream o;
    bool failed = false;

    if(PySequence_Check(first_element) & !PyUnicode_Check(first_element))
    {
        if(y_dim > 0)
        {
            if(len != y_dim)
            {
                o << att_name << ": cannot covert list: given dim_y" << y_dim << " is not equal to the size " << len
                  << "of given list " << std::ends;

                failed = true;
            }
        }
        else
        {
            y_dim = len;
        }
        len = (long) PySequence_Size(first_element);
    }
    else if(y_dim > 0)
    {
        o << att_name << ": cannot covert list: dim_y was given for 1D list" << std::ends;

        failed = true;
    }

    if(x_dim > 0)
    {
        if(len != x_dim)
        {
            o << att_name << ": cannot covert list: given dim_x" << x_dim << " is not equal to the size " << len
              << "of given list " << std::ends;

            failed = true;
        }
    }
    else
    {
        x_dim = len;
    }

    Py_XDECREF(first_element);

    if(failed)
    {
        Tango::Except::throw_exception("PyDs_WrongListSizeForAttribute", o.str(), "set_value()");
    }
}

template <long tangoTypeConst>
inline void __set_write_value_array(Tango::WAttribute &att, bopy::object &seq, long x_dim, long y_dim)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    typedef typename TANGO_const2arraytype(tangoTypeConst) TangoArrayType;

    PyObject *seq_ptr = seq.ptr();
    __check_array_length(seq_ptr, x_dim, y_dim, att.get_name());

    TangoScalarType *tg_ptr;

    // The boost extract could be used to convert:
    // TangoScalarType val = bopy::extract<TangoScalarType>(elt_ptr);
    // the problem is that extract is considerably slower than our
    // convert function which only has to deal with the specific tango
    // data types

    if(y_dim > 0)
    {
        tg_ptr = TangoArrayType::allocbuf(x_dim * y_dim);
        for(long idy = 0; idy < y_dim; ++idy)
        {
            PyObject *row_ptr = PySequence_GetItem(seq_ptr, idy);

            try
            {
                for(long idx = 0; idx < x_dim; ++idx)
                {
                    PyObject *elt_ptr = PySequence_GetItem(row_ptr, idx);
                    try
                    {
                        TangoScalarType tg_scalar;
                        from_py<tangoTypeConst>::convert(elt_ptr, tg_scalar);
                        tg_ptr[idy * x_dim + idx] = tg_scalar;
                        Py_DECREF(elt_ptr);
                    }
                    catch(...)
                    {
                        Py_DECREF(elt_ptr);
                        delete[] tg_ptr;
                        throw;
                    }
                }
                Py_DECREF(row_ptr);
            }
            catch(...)
            {
                Py_DECREF(row_ptr);
                throw;
            }
        }
    }
    else
    {
        tg_ptr = TangoArrayType::allocbuf(x_dim);
        for(long idx = 0; idx < x_dim; ++idx)
        {
            PyObject *elt_ptr = PySequence_GetItem(seq_ptr, idx);
            try
            {
                TangoScalarType tg_scalar;
                from_py<tangoTypeConst>::convert(elt_ptr, tg_scalar);
                tg_ptr[idx] = tg_scalar;
                Py_DECREF(elt_ptr);
            }
            catch(...)
            {
                Py_DECREF(elt_ptr);
                delete[] tg_ptr;
                throw;
            }
        }
    }

    try
    {
        att.set_write_value(tg_ptr, x_dim, y_dim);
        delete[] tg_ptr;
    }
    catch(...)
    {
        delete[] tg_ptr;
        throw;
    }
}

template <>
inline void
    __set_write_value_array<Tango::DEV_STRING>(Tango::WAttribute &att, bopy::object &seq, long x_dim, long y_dim)
{
    PyObject *seq_ptr = seq.ptr();
    __check_array_length(seq_ptr, x_dim, y_dim, att.get_name());

    Tango::DevString *tg_ptr;

    // The boost extract could be used to convert:
    // TangoScalarType val = bopy::extract<TangoScalarType>(elt_ptr);
    // the problem is that extract is considerably slower than our
    // convert function which only has to deal with the specific tango
    // data types

    if(y_dim > 0)
    {
        tg_ptr = Tango::DevVarStringArray::allocbuf(x_dim * y_dim);
        for(long idy = 0; idy < y_dim; ++idy)
        {
            PyObject *row_ptr = PySequence_GetItem(seq_ptr, idy);

            try
            {
                for(long idx = 0; idx < x_dim; ++idx)
                {
                    PyObject *elt_ptr = PySequence_GetItem(row_ptr, idx);
                    try
                    {
                        Tango::DevString tg_scalar;
                        from_py<Tango::DEV_STRING>::convert(elt_ptr, tg_scalar);
                        tg_ptr[idy * x_dim + idx] = Tango::string_dup(tg_scalar);
                        Py_DECREF(elt_ptr);
                    }
                    catch(...)
                    {
                        Py_DECREF(elt_ptr);
                        delete[] tg_ptr;
                        throw;
                    }
                }
                Py_DECREF(row_ptr);
            }
            catch(...)
            {
                Py_DECREF(row_ptr);
                throw;
            }
        }
    }
    else
    {
        tg_ptr = Tango::DevVarStringArray::allocbuf(x_dim);
        for(long idx = 0; idx < x_dim; ++idx)
        {
            PyObject *elt_ptr = PySequence_GetItem(seq_ptr, idx);
            try
            {
                Tango::DevString tg_scalar;
                from_py<Tango::DEV_STRING>::convert(elt_ptr, tg_scalar);
                tg_ptr[idx] = Tango::string_dup(tg_scalar);
                Py_DECREF(elt_ptr);
            }
            catch(...)
            {
                Py_DECREF(elt_ptr);
                delete[] tg_ptr;
                throw;
            }
        }
    }

    try
    {
        att.set_write_value(tg_ptr, x_dim, y_dim);
        //            delete [] tg_ptr;
    }
    catch(...)
    {
        delete[] tg_ptr;
        throw;
    }
}

template <>
inline void
    __set_write_value_array<Tango::DEV_ENCODED>(Tango::WAttribute &att, bopy::object &seq, long x_dim, long y_dim)
{
    Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute",
                                   "set_write_value is not supported for DEV_ENCODED attributes.",
                                   "set_write_value()");
}

inline void set_write_value(Tango::WAttribute &att, bopy::object &value)
{
    long type = att.get_data_type();
    Tango::AttrDataFormat format = att.get_data_format();

    if(format == Tango::SCALAR)
    {
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_write_value_scalar, att, value);
    }
    else
    {
        if(!PySequence_Check(value.ptr()))
        {
            TangoSys_OMemStream o;
            o << "Wrong Python type for attribute " << att.get_name() << "of type " << Tango::CmdArgTypeName[type]
              << ". Expected a sequence." << std::ends;

            Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), "set_value()");
        }
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_write_value_array, att, value, 0, 0);
    }
}

inline void set_write_value(Tango::WAttribute &att, bopy::object &value, long x)
{
    long type = att.get_data_type();
    Tango::AttrDataFormat format = att.get_data_format();

    if(format == Tango::SCALAR || format == Tango::IMAGE)
    {
        std::string attr_type;
        if(format == Tango::SCALAR)
        {
            attr_type = "scalar";
        }
        else
        {
            attr_type = "image";
        }
        TangoSys_OMemStream o;
        o << "Cannot call set_value(data, dim_x) on " << attr_type << " attribute " << att.get_name()
          << ". Use set_write_value(data) instead" << std::ends;

        Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), "set_write_value()");
    }
    else
    {
        if(!PySequence_Check(value.ptr()))
        {
            TangoSys_OMemStream o;
            o << "Wrong Python type for attribute " << att.get_name() << "of type " << Tango::CmdArgTypeName[type]
              << ". Expected a sequence" << std::ends;

            Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), "set_write_value()");
        }
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_write_value_array, att, value, x, 0);
    }
}

inline void set_write_value(Tango::WAttribute &att, bopy::object &value, long x, long y)
{
    long type = att.get_data_type();
    Tango::AttrDataFormat format = att.get_data_format();

    if(format == Tango::SCALAR || format == Tango::SPECTRUM)
    {
        std::string attr_type;
        if(format == Tango::SCALAR)
        {
            attr_type = "scalar";
        }
        else
        {
            attr_type = "spectrum";
        }
        TangoSys_OMemStream o;
        o << "Cannot call set_write_value(data, dim_x, dim_y) "
          << "on " << attr_type << " attribute " << att.get_name() << ". Use set_write_value(data) instead"
          << std::ends;

        Tango::Except::throw_exception(
            (const char *) "PyDs_WrongPythonDataTypeForAttribute", o.str(), (const char *) "set_write_value()");
    }
    else
    {
        if(!PySequence_Check(value.ptr()))
        {
            TangoSys_OMemStream o;
            o << "Wrong Python type for attribute " << att.get_name() << "of type " << Tango::CmdArgTypeName[type]
              << ". Expected a sequence" << std::ends;

            Tango::Except::throw_exception(
                (const char *) "PyDs_WrongPythonDataTypeForAttribute", o.str(), (const char *) "set_write_value()");
        }
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_write_value_array, att, value, x, y);
    }
}

/// @}

/// @name get_write_value
/// @{

template <long tangoTypeConst>
void __get_write_value_scalar(Tango::WAttribute &att, bopy::object *obj)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType v;
    att.get_write_value(v);
    *obj = bopy::object(v);
}

template <>
void __get_write_value_scalar<Tango::DEV_STRING>(Tango::WAttribute &att, bopy::object *obj)
{
    Tango::DevString v = NULL;
    att.get_write_value(v);

    if(v == NULL)
    {
        *obj = bopy::object();
    }
    else
    {
        *obj = from_char_to_boost_str(v);
    }
}

template <long tangoTypeConst>
void __get_write_value_array_pytango3(Tango::WAttribute &att, bopy::object *obj)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    const TangoScalarType *buffer = NULL;
    att.get_write_value(buffer);

    if(buffer == NULL)
    {
        *obj = bopy::list();
        return;
    }

    size_t length = att.get_write_value_length();

    bopy::list o;
    for(size_t n = 0; n < length; ++n)
    {
        o.append(buffer[n]);
    }
    *obj = o;
}

template <>
void __get_write_value_array_pytango3<Tango::DEV_STRING>(Tango::WAttribute &att, bopy::object *obj)
{
    const Tango::ConstDevString *ptr = NULL;

    if(ptr == NULL)
    {
        *obj = bopy::list();
        return;
    }

    long length = att.get_write_value_length();
    att.get_write_value(ptr);
    bopy::list o;
    for(long l = 0; l < length; ++l)
    {
        o.append(from_char_to_boost_str(ptr[l]));
    }
}

template <long tangoTypeConst>
void __get_write_value_array_lists(Tango::WAttribute &att, bopy::object *obj)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    const TangoScalarType *buffer = NULL;
    att.get_write_value(buffer);

    if(buffer == NULL)
    {
        *obj = bopy::list();
        return;
    }

    size_t dim_x = att.get_w_dim_x();
    size_t dim_y = att.get_w_dim_y();

    bopy::list result;

    if(att.get_data_format() == Tango::SPECTRUM)
    {
        for(size_t x = 0; x < dim_x; ++x)
        {
            result.append(buffer[x]);
        }
    }
    else
    {
        for(size_t y = 0; y < dim_y; ++y)
        {
            bopy::list row;
            for(size_t x = 0; x < dim_x; ++x)
            {
                row.append(buffer[x + y * dim_x]);
            }
            result.append(row);
        }
    }
    *obj = result;
}

template <>
void __get_write_value_array_lists<Tango::DEV_STRING>(Tango::WAttribute &att, bopy::object *obj)
{
    const Tango::ConstDevString *buffer = NULL;
    att.get_write_value(buffer);

    if(buffer == NULL)
    {
        *obj = bopy::list();
        return;
    }

    size_t dim_x = att.get_w_dim_x();
    size_t dim_y = att.get_w_dim_y();

    bopy::list result;

    if(att.get_data_format() == Tango::SPECTRUM)
    {
        for(size_t x = 0; x < dim_x; ++x)
        {
            result.append(from_char_to_boost_str(buffer[x]));
        }
    }
    else
    {
        for(size_t y = 0; y < dim_y; ++y)
        {
            bopy::list row;
            for(size_t x = 0; x < dim_x; ++x)
            {
                row.append(from_char_to_boost_str(buffer[x + y * dim_x]));
            }
            result.append(row);
        }
    }
    *obj = result;
}

/// @}
} // namespace PyWAttribute

#include "wattribute_numpy.hpp"

namespace PyWAttribute
{

/// @name get_write_value
/// @{
inline bopy::object get_write_value(Tango::WAttribute &att, PyTango::ExtractAs extract_as)
{
    long type = att.get_data_type();
    bopy::object value;

    Tango::AttrDataFormat fmt = att.get_data_format();

    const bool isScalar = fmt == Tango::SCALAR;

    if(isScalar)
    {
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __get_write_value_scalar, att, &value);
    }
    else
    {
        switch(extract_as)
        {
        case PyTango::ExtractAsPyTango3:
        {
            TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __get_write_value_array_pytango3, att, &value);
            break;
        }
        case PyTango::ExtractAsNumpy:
        {
            TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __get_write_value_array_numpy, att, &value);
            break;
        }
        case PyTango::ExtractAsList:
        {
            TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __get_write_value_array_lists, att, &value);
            break;
        }
        default:
            Tango::Except::throw_exception("PyDs_WrongParameterValue",
                                           "This extract method is not supported by the function.",
                                           "PyWAttribute::get_write_value()");
        }
    }
    return value;
}

/// @}

}; // namespace PyWAttribute

void export_wattribute()
{
    bopy::class_<Tango::WAttribute, bopy::bases<Tango::Attribute>, boost::noncopyable>("WAttribute", bopy::no_init)
        .def("get_min_value", (PyObject * (*) (Tango::WAttribute &) ) & PyWAttribute::get_min_value)
        .def("get_max_value", (PyObject * (*) (Tango::WAttribute &) ) & PyWAttribute::get_max_value)
        .def("set_min_value", &PyWAttribute::set_min_value)
        .def("set_max_value", &PyWAttribute::set_max_value)
        .def("is_min_value", &Tango::WAttribute::is_min_value)
        .def("is_max_value", &Tango::WAttribute::is_max_value)
        .def("get_write_value_length", &Tango::WAttribute::get_write_value_length)
        .def("set_write_value", (void (*)(Tango::WAttribute &, bopy::object &)) & PyWAttribute::set_write_value)
        .def("set_write_value", (void (*)(Tango::WAttribute &, bopy::object &, long)) & PyWAttribute::set_write_value)
        .def("set_write_value",
             (void (*)(Tango::WAttribute &, bopy::object &, long, long)) & PyWAttribute::set_write_value)
        .def("get_write_value",
             &PyWAttribute::get_write_value,
             (arg_("self"), arg_("extract_as") = PyTango::ExtractAsNumpy));
}
