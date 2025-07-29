/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "pytgutils.h"
#include "fast_from_py.h"
#include "to_py_numpy.hpp"

namespace PyDeviceData
{

Tango::CmdArgType get_type(Tango::DeviceData &self)
{
    /// @todo This should change in Tango itself, get_type should not return int!!
    return static_cast<Tango::CmdArgType>(self.get_type());
}

/// @name Scalar Insertion
/// @{
template <long tangoTypeConst>
void insert_scalar(Tango::DeviceData &self, bopy::object py_value)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    TangoScalarType value;
    from_py<tangoTypeConst>::convert(py_value.ptr(), value);
    self << value;
}

template <>
void insert_scalar<Tango::DEV_STRING>(Tango::DeviceData &self, bopy::object py_value)
{
    PyObject *py_value_ptr = py_value.ptr();
    if(PyUnicode_Check(py_value_ptr))
    {
        PyObject *obj_bytes_ptr = EncodeAsLatin1(py_value_ptr);
        Tango::DevString value = PyBytes_AsString(obj_bytes_ptr);
        self << value;
        Py_DECREF(obj_bytes_ptr);
    }
    else if(PyBytes_Check(py_value_ptr))
    {
        Tango::DevString value = PyBytes_AsString(py_value_ptr);
        self << value;
    }
    else
    {
        raise_(PyExc_TypeError, "can't translate python object to C char* in insert_scalar<Tango::DEV_STRING>");
    }
}

template <>
void insert_scalar<Tango::DEV_ENCODED>(Tango::DeviceData &self, bopy::object py_value)
{
    Tango::DevEncoded val;
    bopy::object p0 = py_value[0];
    const char *encoded_format = bopy::extract<const char *>(p0.ptr());
    val.encoded_format = CORBA::string_dup(encoded_format);

    view_pybytes_as_char_array(py_value[1], val.encoded_data);
    // By giving a value (not a pointer) to << the data will be copied by CORBA

    self << val;
}

template <>
void insert_scalar<Tango::DEV_VOID>(Tango::DeviceData &self, bopy::object py_value)
{
    raise_(PyExc_TypeError, "Trying to insert a value in a DEV_VOID DeviceData!");
}

template <>
void insert_scalar<Tango::DEV_PIPE_BLOB>(Tango::DeviceData &self, bopy::object py_value)
{
    assert(false);
}

/// @}
// ~Scalar Insertion
// -----------------------------------------------------------------------

/// @name Array Insertion
/// @{
template <long tangoArrayTypeConst>
void insert_array(Tango::DeviceData &self, bopy::object py_value)
{
    typedef typename TANGO_const2type(tangoArrayTypeConst) TangoArrayType;

    // self << val; -->> This ends up doing:
    // inline void operator << (DevVarUShortArray* datum)
    // { any.inout() <<= datum;}
    // So:
    //  - We loose ownership of the pointer, should not remove it
    //  - it's a CORBA object who gets ownership, not a buggy Tango
    //    thing. So the last parameter to fast_convert2array is false
    TangoArrayType *val = fast_convert2array<tangoArrayTypeConst>(py_value);
    self << val;
}

/// @}
// ~Array Insertion
// -----------------------------------------------------------------------

/// @name Scalar Extraction
/// @{
template <long tangoTypeConst>
bopy::object extract_scalar(Tango::DeviceData &self)
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    /// @todo CONST_DEV_STRING ell el tracta com DEV_STRING
    TangoScalarType val;
    self >> val;
    return bopy::object(val);
}

template <>
bopy::object extract_scalar<Tango::DEV_VOID>(Tango::DeviceData &self)
{
    return bopy::object();
}

template <>
bopy::object extract_scalar<Tango::DEV_STRING>(Tango::DeviceData &self)
{
    typedef std::string TangoScalarType;
    TangoScalarType val;
    self >> val;
    return from_char_to_boost_str(val);
}

template <>
bopy::object extract_scalar<Tango::DEV_PIPE_BLOB>(Tango::DeviceData &self)
{
    assert(false);
    return bopy::object();
}

/// @}
// ~Scalar Extraction
// -----------------------------------------------------------------------

/// @name Array extraction
/// @{

template <long tangoArrayTypeConst>
bopy::object extract_array(Tango::DeviceData &self, bopy::object &py_self, PyTango::ExtractAs extract_as)
{
    typedef typename TANGO_const2type(tangoArrayTypeConst) TangoArrayType;

    // const is the pointed, not the pointer. So cannot modify the data.
    // And that's because the data is still inside "self" after extracting.
    // This also means that we are not supposed to "delete" tmp_ptr.
    const TangoArrayType *tmp_ptr;
    self >> tmp_ptr;

    switch(extract_as)
    {
    default:
    case PyTango::ExtractAsNumpy:
        return to_py_numpy<tangoArrayTypeConst>(tmp_ptr, py_self);
    case PyTango::ExtractAsList:
    case PyTango::ExtractAsPyTango3:
        return to_py_list(tmp_ptr);
    case PyTango::ExtractAsTuple:
        return to_py_tuple(tmp_ptr);
    case PyTango::ExtractAsString: /// @todo
    case PyTango::ExtractAsNothing:
        return bopy::object();
    }
}

template <>
bopy::object extract_array<Tango::DEVVAR_STATEARRAY>(Tango::DeviceData &self,
                                                     bopy::object &py_self,
                                                     PyTango::ExtractAs extract_as)
{
    assert(false);
    return bopy::object();
}

/// @}
// ~Array Extraction
// -----------------------------------------------------------------------

bopy::object extract(bopy::object py_self, PyTango::ExtractAs extract_as)
{
    Tango::DeviceData &self = bopy::extract<Tango::DeviceData &>(py_self);

    TANGO_DO_ON_DEVICE_DATA_TYPE_ID(self.get_type(), return extract_scalar<tangoTypeConst>(self);
                                    , return extract_array<tangoTypeConst>(self, py_self, extract_as););
    return bopy::object();
}

void insert(Tango::DeviceData &self, long data_type, bopy::object py_value)
{
    TANGO_DO_ON_DEVICE_DATA_TYPE_ID(data_type, insert_scalar<tangoTypeConst>(self, py_value);
                                    , insert_array<tangoTypeConst>(self, py_value););
}
} // namespace PyDeviceData

void export_device_data()
{
    bopy::class_<Tango::DeviceData> DeviceData("DeviceData", bopy::init<>());

    bopy::scope scope_dd = DeviceData;

    /// @todo get rid of except_flags everywhere... or really use and export them everywhere!
    bopy::enum_<Tango::DeviceData::except_flags>("except_flags")
        .value("isempty_flag", Tango::DeviceData::isempty_flag)
        .value("wrongtype_flag", Tango::DeviceData::wrongtype_flag)
        .value("numFlags", Tango::DeviceData::numFlags);

    DeviceData
        .def(bopy::init<const Tango::DeviceData &>())

        .def("extract", &PyDeviceData::extract, (arg_("self"), arg_("extract_as") = PyTango::ExtractAsNumpy))

        .def("insert", &PyDeviceData::insert, (arg_("self"), arg_("data_type"), arg_("value")))

        /// @todo do not throw exceptions!!
        .def("is_empty", &Tango::DeviceData::is_empty)

        // TODO
        //	void exceptions(bitset<numFlags> fl) {exceptions_flags = fl;}
        //	bitset<numFlags> exceptions() {return exceptions_flags;}
        //	void reset_exceptions(except_flags fl) {exceptions_flags.reset((size_t)fl);}
        //	void set_exceptions(except_flags fl) {exceptions_flags.set((size_t)fl);}

        .def("get_type", &PyDeviceData::get_type);
}
