/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"
#include "attribute.h"
#include "fast_from_py.h"

#ifdef WIN32
  #define PYTG_TIME_FROM_DOUBLE(dbl, tv)                           \
      if(true)                                                     \
      {                                                            \
          tv.time = (time_t) floor(dbl);                           \
          tv.millitm = (unsigned short) ((dbl - tv.time) * 1.0e3); \
      }                                                            \
      else                                                         \
          (void) 0
  #define PYTG_NEW_TIME_FROM_DOUBLE(dbl, tv) \
      struct _timeb tv;                      \
      PYTG_TIME_FROM_DOUBLE(dbl, tv)
#else
  #define PYTG_TIME_FROM_DOUBLE(dbl, tv) double2timeval(tv, dbl);
  #define PYTG_NEW_TIME_FROM_DOUBLE(dbl, tv) \
      struct timeval tv;                     \
      PYTG_TIME_FROM_DOUBLE(dbl, tv)
#endif

inline static void throw_wrong_python_data_type(const std::string &att_name, const char *method)
{
    TangoSys_OMemStream o;
    o << "Wrong Python type for attribute " << att_name << std::ends;
    Tango::Except::throw_exception((const char *) "PyDs_WrongPythonDataTypeForAttribute", o.str(), method);
}

inline static void throw_wrong_python_data_type_in_array(const std::string &att_name, long idx, const char *method)
{
    TangoSys_OMemStream o;
    o << "Wrong Python type for attribute " << att_name << ".\nElement with index " << idx << " in sequence does not "
      << "have a correct type." << std::ends;

    Tango::Except::throw_exception((const char *) "PyDs_WrongPythonDataTypeForAttribute", o.str(), method);
}

extern long TANGO_VERSION_HEX;

namespace PyAttribute
{
/**
 * Tango Attribute set_value wrapper for scalar attributes
 *
 * @param att attribute reference
 * @param value new attribute value
 */
template <long tangoTypeConst>
inline void __set_value_scalar(Tango::Attribute &att, bopy::object &value)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    /*
       I hate doing this because tango inside is doing a new again when
       set_value_date_quality is invoked with the release flag to true
       the other option would be to use per thread tango data like it was
       done in v3.0.4
       I prefer this one since it decouples TangoC++ from PyTango and creating
       a scalar is not so expensive after all
    */
    unique_pointer<TangoScalarType> cpp_val(new TangoScalarType);

    from_py<tangoTypeConst>::convert(value.ptr(), *cpp_val);
    att.set_value(cpp_val.release(), 1, 0, true);
}

/**
 * Tango Attribute set_value wrapper for DevEncoded attributes
 *
 * @param att attribute reference
 * @param encoding_str new attribute encoding info
 * @param data_str new attribute data
 */
inline void __set_value(Tango::Attribute &att, bopy::str &encoding_str, bopy::str &data_str)
{
    Tango::DevString encoding_char = from_str_to_char(encoding_str);
    Py_ssize_t size;
    Tango::DevString data_char = from_str_to_char(data_str, &size, true);

    att.set_value(&encoding_char, (Tango::DevUChar *) data_char, (long) size, true);
}

/**
 * Tango Attribute set_value wrapper for DevEncoded attributes
 *
 * @param att attribute reference
 * @param data_str new attribute data string
 * @param data new attribute data
 */
inline void __set_value(Tango::Attribute &att, bopy::str &encoding_str, bopy::object &data_obj)
{
    Tango::DevString encoding_char = from_str_to_char(encoding_str);
    Py_ssize_t size;
    Tango::DevString data_char = from_str_to_char(data_obj, &size, true);

    att.set_value(&encoding_char, (Tango::DevUChar *) data_char, (long) size, true);
}

/**
 * Tango Attribute set_value_date_quality wrapper for scalar attributes
 *
 * @param att attribute reference
 * @param value new attribute value
 * @param t timestamp
 * @param quality attribute quality
 */
template <long tangoTypeConst>
inline void
    __set_value_date_quality_scalar(Tango::Attribute &att, bopy::object &value, double t, Tango::AttrQuality quality)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    PYTG_NEW_TIME_FROM_DOUBLE(t, tv);

    /*
       I hate doing because tango inside is doing a new again when
       set_value_date_quality is invoked with the release flag to true
       the other option would be to use per thread tango data like it was
       done in v3.0.4
       I prefer this one since it decouples TangoC++ from PyTango and creating
       a scalar is not so expensive after all
    */
    unique_pointer<TangoScalarType> cpp_val(new TangoScalarType);

    from_py<tangoTypeConst>::convert(value, *cpp_val);
    att.set_value_date_quality(cpp_val.release(), tv, quality, 1, 0, true);
}

/**
 * Tango Attribute set_value_date_quality wrapper for DevEncoded attributes
 *
 * @param att attribute reference
 * @param encoding_str new attribute data string
 * @param data_str new attribute data
 * @param t timestamp
 * @param quality attribute quality
 */
inline void __set_value_date_quality(
    Tango::Attribute &att, bopy::str &encoding_str, bopy::str &data_str, double t, Tango::AttrQuality quality)
{
    Tango::DevString encoding_char = from_str_to_char(encoding_str);
    Py_ssize_t size;
    Tango::DevString data_char = from_str_to_char(data_str, &size, true);

    PYTG_NEW_TIME_FROM_DOUBLE(t, tv);

    att.set_value_date_quality(&encoding_char, (Tango::DevUChar *) data_char, (long) size, tv, quality, true);
}

/**
 * Tango Attribute set_value_date_quality wrapper for DevEncoded attributes
 *
 * @param att attribute reference
 * @param encoding_str new attribute data string
 * @param data_obj new attribute data
 * @param t timestamp
 * @param quality attribute quality
 */
inline void __set_value_date_quality(
    Tango::Attribute &att, bopy::str &encoding_str, bopy::object &data_obj, double t, Tango::AttrQuality quality)
{
    Tango::DevString encoding_char = from_str_to_char(encoding_str);
    Py_ssize_t size;
    Tango::DevString data_char = from_str_to_char(data_obj, &size, true);

    PYTG_NEW_TIME_FROM_DOUBLE(t, tv);

    att.set_value_date_quality(&encoding_char, (Tango::DevUChar *) data_char, (long) size, tv, quality, true);
}

template <long tangoTypeConst>
void __set_value_date_quality_array(Tango::Attribute &att,
                                    bopy::object &value,
                                    double time,
                                    Tango::AttrQuality *quality,
                                    long *x,
                                    long *y,
                                    const std::string &fname,
                                    bool isImage)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    if(!PySequence_Check(value.ptr()))
    {
        TangoSys_OMemStream o;
        o << "Wrong Python type for attribute " << att.get_name() << " of type "
          << Tango::CmdArgTypeName[tangoTypeConst] << ". Expected a sequence." << std::ends;

        TangoSys_OMemStream origin;
        origin << TANGO_EXCEPTION_ORIGIN << std::ends;

        Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), origin.str());
    }

    TangoScalarType *data_buffer;

    long res_dim_x = 0, res_dim_y = 0;
    data_buffer =
        fast_python_to_tango_buffer_numpy<tangoTypeConst>(value.ptr(), x, y, fname, isImage, res_dim_x, res_dim_y);

    static const bool release = true;

    if(quality)
    {
        PYTG_NEW_TIME_FROM_DOUBLE(time, tv);
        att.set_value_date_quality(data_buffer, tv, *quality, res_dim_x, res_dim_y, release);
    }
    else
    {
        att.set_value(data_buffer, res_dim_x, res_dim_y, release);
    }
}

inline void __set_value(const std::string &fname,
                        Tango::Attribute &att,
                        bopy::object &value,
                        long *x,
                        long *y,
                        double t = 0.0,
                        Tango::AttrQuality *quality = 0)
{
    long type = att.get_data_type();
    Tango::AttrDataFormat format = att.get_data_format();

    const bool isScalar = (format == Tango::SCALAR);
    const bool isImage = (format == Tango::IMAGE);

    if(isScalar)
    {
        if((x && ((*x) > 1)) || (y && (*y) > 0))
        {
            TangoSys_OMemStream o;
            o << "Cannot call " << fname;
            if(y)
            {
                o << "(data, dim_x, dim_y) on scalar attribute ";
            }
            else
            {
                o << "(data, dim_x) on scalar attribute ";
            }

            if(quality)
            {
                o << att.get_name() << ". Use set_value_date_quality(data) instead" << std::ends;
            }
            else
            {
                o << att.get_name() << ". Use set_value(data) instead" << std::ends;
            }

            TangoSys_OMemStream origin;
            origin << TANGO_EXCEPTION_ORIGIN << std::ends;

            Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), origin.str());
        }
        else
        {
            if(quality)
            {
                TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_value_date_quality_scalar, att, value, t, *quality);
            }
            else
            {
                TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(type, __set_value_scalar, att, value);
            }
        }
    }
    else
    {
        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(
            type, __set_value_date_quality_array, att, value, t, quality, x, y, fname, isImage);
    }
}

inline void __set_value(const std::string &fname,
                        Tango::Attribute &att,
                        bopy::str &data_str,
                        bopy::str &data,
                        double t = 0.0,
                        Tango::AttrQuality *quality = 0)
{
    if(quality)
    {
        __set_value_date_quality(att, data_str, data, t, *quality);
    }
    else
    {
        __set_value(att, data_str, data);
    }
}

inline void __set_value(const std::string &fname,
                        Tango::Attribute &att,
                        bopy::str &data_str,
                        bopy::object &data,
                        double t = 0.0,
                        Tango::AttrQuality *quality = 0)
{
    if(quality)
    {
        __set_value_date_quality(att, data_str, data, t, *quality);
    }
    else
    {
        __set_value(att, data_str, data);
    }
}

inline void set_value(Tango::Attribute &att, bopy::object &value)
{
    __set_value("set_value", att, value, 0, 0);
}

inline void set_value(Tango::Attribute &att, Tango::EncodedAttribute *data)
{
    if(data == NULL)
    {
        TangoSys_OMemStream description;
        description << "Data pointer for attribute " << att.get_name()
                    << " is NULL! Most probably set_value was called with None ";

        TangoSys_OMemStream origin;
        origin << TANGO_EXCEPTION_ORIGIN << std::ends;

        Tango::Except::throw_exception("PyDs_AttributeDataIsNULL", description.str(), origin.str());
    }

    Tango::DevString *f = data->get_format();
    Tango::DevUChar *d = data->get_data();
    long size = data->get_size();

    if(*f == NULL)
    {
        TangoSys_OMemStream o;
        o << "DevEncoded format for attribute " << att.get_name() << " not specified" << std::ends;

        TangoSys_OMemStream origin;
        origin << TANGO_EXCEPTION_ORIGIN << std::ends;

        Tango::Except::throw_exception("PyDs_DevEncodedFormatNotSpecified", o.str(), origin.str());
    }

    if(size == 0 || !d)
    {
        TangoSys_OMemStream o;
        o << "DevEncoded data for attribute " << att.get_name() << " not specified" << std::ends;

        TangoSys_OMemStream origin;
        origin << TANGO_EXCEPTION_ORIGIN << std::ends;

        Tango::Except::throw_exception("PyDs_DevEncodedDataNotSpecified", o.str(), origin.str());
    }

    Tango::DevString f_copy = Tango::string_dup(*f);

    Tango::DevUChar *d_copy = new Tango::DevUChar[size];
    memcpy(d_copy, d, size);

    att.set_value(&f_copy, d_copy, size, true);
}

inline void set_value(Tango::Attribute &att, bopy::str &data_str, bopy::str &data)
{
    __set_value("set_value", att, data_str, data);
}

inline void set_value(Tango::Attribute &att, bopy::str &data_str, bopy::object &data)
{
    __set_value("set_value", att, data_str, data);
}

inline void set_value(Tango::Attribute &att, bopy::object &value, long x)
{
    __set_value("set_value", att, value, &x, 0);
}

inline void set_value(Tango::Attribute &att, bopy::object &value, long x, long y)
{
    __set_value("set_value", att, value, &x, &y);
}

inline void set_value_date_quality(Tango::Attribute &att, bopy::object &value, double t, Tango::AttrQuality quality)
{
    __set_value("set_value_date_quality", att, value, 0, 0, t, &quality);
}

inline void set_value_date_quality(
    Tango::Attribute &att, bopy::str &data_str, bopy::str &data, double t, Tango::AttrQuality quality)
{
    __set_value("set_value_date_quality", att, data_str, data, t, &quality);
}

inline void set_value_date_quality(
    Tango::Attribute &att, bopy::str &data_str, bopy::object &data, double t, Tango::AttrQuality quality)
{
    __set_value("set_value_date_quality", att, data_str, data, t, &quality);
}

inline void
    set_value_date_quality(Tango::Attribute &att, bopy::object &value, double t, Tango::AttrQuality quality, long x)
{
    __set_value("set_value_date_quality", att, value, &x, 0, t, &quality);
}

inline void set_value_date_quality(
    Tango::Attribute &att, bopy::object &value, double t, Tango::AttrQuality quality, long x, long y)
{
    __set_value("set_value_date_quality", att, value, &x, &y, t, &quality);
}

template <typename TangoScalarType>
inline void _get_properties_multi_attr_prop(Tango::Attribute &att, bopy::object &multi_attr_prop)
{
    Tango::MultiAttrProp<TangoScalarType> tg_multi_attr_prop;
    att.get_properties(tg_multi_attr_prop);

    to_py(tg_multi_attr_prop, multi_attr_prop);
}

inline bopy::object get_properties_multi_attr_prop(Tango::Attribute &att, bopy::object &multi_attr_prop)
{
    long tangoTypeConst = att.get_data_type();
    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _get_properties_multi_attr_prop, att, multi_attr_prop);
    return multi_attr_prop;
}

template <typename TangoScalarType>
inline void _set_properties_multi_attr_prop(Tango::Attribute &att, bopy::object &multi_attr_prop)
{
    Tango::MultiAttrProp<TangoScalarType> tg_multi_attr_prop;
    from_py_object(multi_attr_prop, tg_multi_attr_prop);
    att.set_properties(tg_multi_attr_prop);
}

void set_properties_multi_attr_prop(Tango::Attribute &att, bopy::object &multi_attr_prop)
{
    long tangoTypeConst = att.get_data_type();
    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _set_properties_multi_attr_prop, att, multi_attr_prop);
}

void set_upd_properties(Tango::Attribute &att, bopy::object &attr_cfg)
{
    Tango::AttributeConfig_3 tg_attr_cfg;
    from_py_object(attr_cfg, tg_attr_cfg);
    att.set_upd_properties(tg_attr_cfg);
}

void set_upd_properties(Tango::Attribute &att, bopy::object &attr_cfg, bopy::object &dev_name)
{
    Tango::AttributeConfig_3 tg_attr_cfg;
    from_py_object(attr_cfg, tg_attr_cfg);
    std::string tg_dev_name = bopy::extract<std::string>(dev_name);
    att.set_upd_properties(tg_attr_cfg, tg_dev_name);
}

inline void fire_change_event(Tango::Attribute &self)
{
    self.fire_change_event();
}

inline void fire_change_event(Tango::Attribute &self, bopy::object &data)
{
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        self.fire_change_event(const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    TangoSys_OMemStream o;
    o << "Wrong Python argument type for attribute " << self.get_name() << ". Expected a DevFailed." << std::ends;

    TangoSys_OMemStream origin;
    origin << TANGO_EXCEPTION_ORIGIN << std::ends;

    Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), origin.str());
}

inline void fire_alarm_event(Tango::Attribute &self)
{
    self.fire_alarm_event();
}

inline void fire_alarm_event(Tango::Attribute &self, bopy::object &data)
{
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        self.fire_alarm_event(const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    TangoSys_OMemStream o;
    o << "Wrong Python argument type for attribute " << self.get_name() << ". Expected a DevFailed." << std::ends;

    TangoSys_OMemStream origin;
    origin << TANGO_EXCEPTION_ORIGIN << std::ends;

    Tango::Except::throw_exception("PyDs_WrongPythonDataTypeForAttribute", o.str(), origin.str());
}

// usually not necessary to rewrite but with direct declaration the compiler
// gives an error. It seems to be because the tango method definition is not
// in the header file.
inline bool is_polled(Tango::Attribute &self)
{
    return self.is_polled();
}

template <typename TangoScalarType>
inline void _set_min_alarm(Tango::Attribute &self, bopy::object value)
{
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_min_alarm(c_value);
}

inline void set_min_alarm(Tango::Attribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_min_alarm(value_convert());
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

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _set_min_alarm, self, value);
    }
}

template <typename TangoScalarType>
inline void _set_max_alarm(Tango::Attribute &self, bopy::object value)
{
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_max_alarm(c_value);
}

inline void set_max_alarm(Tango::Attribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_max_alarm(value_convert());
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

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _set_max_alarm, self, value);
    }
}

template <typename TangoScalarType>
inline void _set_min_warning(Tango::Attribute &self, bopy::object value)
{
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_min_warning(c_value);
}

inline void set_min_warning(Tango::Attribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_min_warning(value_convert());
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

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _set_min_warning, self, value);
    }
}

template <typename TangoScalarType>
inline void _set_max_warning(Tango::Attribute &self, bopy::object value)
{
    TangoScalarType c_value = bopy::extract<TangoScalarType>(value);
    self.set_max_warning(c_value);
}

inline void set_max_warning(Tango::Attribute &self, bopy::object value)
{
    bopy::extract<std::string> value_convert(value);

    if(value_convert.check())
    {
        self.set_max_warning(value_convert());
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

        TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_NAME(tangoTypeConst, _set_max_warning, self, value);
    }
}

template <long tangoTypeConst>
PyObject *__get_min_alarm(Tango::Attribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_min_alarm(tg_val);
    bopy::object py_value(tg_val);

    return bopy::incref(py_value.ptr());
}

PyObject *get_min_alarm(Tango::Attribute &att)
{
    long tangoTypeConst = att.get_data_type();

    if(tangoTypeConst == Tango::DEV_ENCODED)
    {
        tangoTypeConst = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, return __get_min_alarm, att);
    return 0;
}

template <long tangoTypeConst>
PyObject *__get_max_alarm(Tango::Attribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_max_alarm(tg_val);
    bopy::object py_value(tg_val);

    return bopy::incref(py_value.ptr());
}

PyObject *get_max_alarm(Tango::Attribute &att)
{
    long tangoTypeConst = att.get_data_type();

    if(tangoTypeConst == Tango::DEV_ENCODED)
    {
        tangoTypeConst = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, return __get_max_alarm, att);
    return 0;
}

template <long tangoTypeConst>
PyObject *__get_min_warning(Tango::Attribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_min_warning(tg_val);
    bopy::object py_value(tg_val);

    return bopy::incref(py_value.ptr());
}

PyObject *get_min_warning(Tango::Attribute &att)
{
    long tangoTypeConst = att.get_data_type();

    if(tangoTypeConst == Tango::DEV_ENCODED)
    {
        tangoTypeConst = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, return __get_min_warning, att);
    return 0;
}

template <long tangoTypeConst>
PyObject *__get_max_warning(Tango::Attribute &att)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;

    TangoScalarType tg_val;
    att.get_max_warning(tg_val);
    bopy::object py_value(tg_val);

    return bopy::incref(py_value.ptr());
}

PyObject *get_max_warning(Tango::Attribute &att)
{
    long tangoTypeConst = att.get_data_type();

    if(tangoTypeConst == Tango::DEV_ENCODED)
    {
        tangoTypeConst = Tango::DEV_UCHAR;
    }

    TANGO_CALL_ON_ATTRIBUTE_DATA_TYPE_ID(tangoTypeConst, return __get_max_warning, att);
    return 0;
}

}; // namespace PyAttribute

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_quality_overloads, Tango::Attribute::set_quality, 1, 2);

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_change_event_overloads, Tango::Attribute::set_change_event, 1, 2);

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_alarm_event_overloads, Tango::Attribute::set_alarm_event, 1, 2);

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_archive_event_overloads, Tango::Attribute::set_archive_event, 1, 2);

void export_attribute()
{
    bopy::enum_<Tango::Attribute::alarm_flags>("alarm_flags")
        .value("min_level", Tango::Attribute::min_level)
        .value("max_level", Tango::Attribute::max_level)
        .value("rds", Tango::Attribute::rds)
        .value("min_warn", Tango::Attribute::min_warn)
        .value("max_warn", Tango::Attribute::max_warn)
        .value("numFlags", Tango::Attribute::numFlags);

    bopy::class_<Tango::Attribute>("Attribute", bopy::no_init)
        .def("is_write_associated", &Tango::Attribute::is_writ_associated)
        .def("is_min_alarm", &Tango::Attribute::is_min_alarm)
        .def("is_max_alarm", &Tango::Attribute::is_max_alarm)
        .def("is_min_warning", &Tango::Attribute::is_min_warning)
        .def("is_max_warning", &Tango::Attribute::is_max_warning)
        .def("is_rds_alarm", &Tango::Attribute::is_rds_alarm)
        .def("is_polled", &PyAttribute::is_polled)
        .def("check_alarm", &Tango::Attribute::check_alarm)
        .def("get_writable", &Tango::Attribute::get_writable)
        .def("get_name",
             (std::string const &(Tango::Attribute::*) () const) & Tango::Attribute::get_name,
             bopy::return_value_policy<bopy::copy_const_reference>())
        .def("get_data_type", &Tango::Attribute::get_data_type)
        .def("get_data_format", &Tango::Attribute::get_data_format)
        .def("get_assoc_name",
             &Tango::Attribute::get_assoc_name,
             bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("get_assoc_ind", &Tango::Attribute::get_assoc_ind)
        .def("set_assoc_ind", &Tango::Attribute::set_assoc_ind)
        .def("get_date", &Tango::Attribute::get_date, bopy::return_internal_reference<>())
        .def("set_date", (void(Tango::Attribute::*)(Tango::TimeVal &)) & Tango::Attribute::set_date)
        .def("get_label", &Tango::Attribute::get_label, bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("get_quality", &Tango::Attribute::get_quality, bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("set_quality", &Tango::Attribute::set_quality, set_quality_overloads())
        .def("get_data_size", &Tango::Attribute::get_data_size)
        .def("get_x", &Tango::Attribute::get_x)
        .def("get_max_dim_x", &Tango::Attribute::get_max_dim_x)
        .def("get_y", &Tango::Attribute::get_y)
        .def("get_max_dim_y", &Tango::Attribute::get_max_dim_y)
        .def("get_polling_period", &Tango::Attribute::get_polling_period)
        .def("set_attr_serial_model", &Tango::Attribute::set_attr_serial_model)
        .def("get_attr_serial_model", &Tango::Attribute::get_attr_serial_model)

        .def("set_min_alarm", &PyAttribute::set_min_alarm)
        .def("set_max_alarm", &PyAttribute::set_max_alarm)
        .def("set_min_warning", &PyAttribute::set_min_warning)
        .def("set_max_warning", &PyAttribute::set_max_warning)

        .def("get_value_flag", &Tango::Attribute::get_value_flag)
        .def("set_value_flag", &Tango::Attribute::set_value_flag)

        .def("get_disp_level", &Tango::Attribute::get_disp_level)

        .def("change_event_subscribed", &Tango::Attribute::change_event_subscribed)
        .def("alarm_event_subscribed", &Tango::Attribute::alarm_event_subscribed)
        .def("periodic_event_subscribed", &Tango::Attribute::periodic_event_subscribed)
        .def("archive_event_subscribed", &Tango::Attribute::archive_event_subscribed)
        .def("user_event_subscribed", &Tango::Attribute::user_event_subscribed)

        .def("use_notifd_event", &Tango::Attribute::use_notifd_event)
        .def("use_zmq_event", &Tango::Attribute::use_zmq_event)

        .def("get_min_alarm", (PyObject * (*) (Tango::Attribute &) ) & PyAttribute::get_min_alarm)
        .def("get_max_alarm", (PyObject * (*) (Tango::Attribute &) ) & PyAttribute::get_max_alarm)
        .def("get_min_warning", (PyObject * (*) (Tango::Attribute &) ) & PyAttribute::get_min_warning)
        .def("get_max_warning", (PyObject * (*) (Tango::Attribute &) ) & PyAttribute::get_max_warning)

        .def("_set_value", (void (*)(Tango::Attribute &, bopy::object &)) & PyAttribute::set_value)
        .def("_set_value", (void (*)(Tango::Attribute &, bopy::str &, bopy::object &)) & PyAttribute::set_value)
        .def("_set_value", (void (*)(Tango::Attribute &, bopy::str &, bopy::str &)) & PyAttribute::set_value)
        .def("_set_value", (void (*)(Tango::Attribute &, Tango::EncodedAttribute *)) & PyAttribute::set_value)
        .def("_set_value", (void (*)(Tango::Attribute &, bopy::object &, long)) & PyAttribute::set_value)
        .def("_set_value", (void (*)(Tango::Attribute &, bopy::object &, long, long)) & PyAttribute::set_value)
        .def("_set_value_date_quality",
             (void (*)(Tango::Attribute &, bopy::object &, double t, Tango::AttrQuality quality)) &
                 PyAttribute::set_value_date_quality)
        .def("_set_value_date_quality",
             (void (*)(Tango::Attribute &, bopy::str &, bopy::str &, double t, Tango::AttrQuality quality)) &
                 PyAttribute::set_value_date_quality)
        .def("_set_value_date_quality",
             (void (*)(Tango::Attribute &, bopy::str &, bopy::object &, double t, Tango::AttrQuality quality)) &
                 PyAttribute::set_value_date_quality)
        .def("_set_value_date_quality",
             (void (*)(Tango::Attribute &, bopy::object &, double t, Tango::AttrQuality quality, long)) &
                 PyAttribute::set_value_date_quality)
        .def("_set_value_date_quality",
             (void (*)(Tango::Attribute &, bopy::object &, double t, Tango::AttrQuality quality, long, long)) &
                 PyAttribute::set_value_date_quality)

        .def("set_change_event", &Tango::Attribute::set_change_event, set_change_event_overloads())
        .def("set_alarm_event", &Tango::Attribute::set_alarm_event, set_alarm_event_overloads())
        .def("set_archive_event", &Tango::Attribute::set_archive_event, set_archive_event_overloads())

        .def("is_change_event", &Tango::Attribute::is_change_event)
        .def("is_check_change_criteria", &Tango::Attribute::is_check_change_criteria)
        .def("is_alarm_event", &Tango::Attribute::is_alarm_event)
        .def("is_check_alarm_criteria", &Tango::Attribute::is_check_alarm_criteria)
        .def("is_archive_event", &Tango::Attribute::is_archive_event)
        .def("is_check_archive_criteria", &Tango::Attribute::is_check_archive_criteria)
        .def("set_data_ready_event", &Tango::Attribute::set_data_ready_event)
        .def("is_data_ready_event", &Tango::Attribute::is_data_ready_event)
        .def("remove_configuration", &Tango::Attribute::remove_configuration)

        /*
        .def("_get_properties", &PyAttribute::get_properties)
        .def("_get_properties_2", &PyAttribute::get_properties_2)
        .def("_get_properties_3", &PyAttribute::get_properties_3)
        */
        .def("_get_properties_multi_attr_prop", &PyAttribute::get_properties_multi_attr_prop)

        /*
        .def("_set_properties", &PyAttribute::set_properties)
        .def("_set_properties_3", &PyAttribute::set_properties_3)
        */
        .def("_set_properties_multi_attr_prop", &PyAttribute::set_properties_multi_attr_prop)

        .def("set_upd_properties", (void (*)(Tango::Attribute &, bopy::object &)) & PyAttribute::set_upd_properties)

        .def("set_upd_properties",
             (void (*)(Tango::Attribute &, bopy::object &, bopy::object &)) & PyAttribute::set_upd_properties)

        .def("fire_change_event", (void (*)(Tango::Attribute &)) & PyAttribute::fire_change_event)
        .def("fire_change_event", (void (*)(Tango::Attribute &, bopy::object &)) & PyAttribute::fire_change_event)

        .def("fire_alarm_event", (void (*)(Tango::Attribute &)) & PyAttribute::fire_alarm_event)
        .def("fire_alarm_event", (void (*)(Tango::Attribute &, bopy::object &)) & PyAttribute::fire_alarm_event);
}
