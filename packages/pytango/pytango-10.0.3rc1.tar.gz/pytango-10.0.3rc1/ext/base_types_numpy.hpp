/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#pragma once

template <long tangoTypeConst>
struct convert_numpy_to_integer
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    static const long NumpyType = TANGO_const2numpy(tangoTypeConst);

    convert_numpy_to_integer()
    {
        bopy::converter::registry::push_back(&convertible, &construct, bopy::type_id<TangoScalarType>());
    }

    static void *convertible(PyObject *obj)
    {
        if(!PyArray_CheckScalar(obj))
        {
            return 0;
        }

        PyArray_Descr *type = PyArray_DescrFromScalar(obj);
        if(PyDataType_ISINTEGER(type))
        {
            return obj;
        }
        return 0;
    }

    static void construct(PyObject *obj, bopy::converter::rvalue_from_python_stage1_data *data)
    {
        typedef bopy::converter::rvalue_from_python_storage<TangoScalarType> tango_storage;
        void *const storage = reinterpret_cast<tango_storage *>(data)->storage.bytes;
        TangoScalarType *ptr = new(storage) TangoScalarType();

        PyObject *native_obj = PyObject_CallMethod(obj, const_cast<char *>("__int__"), NULL);
        if(native_obj == NULL)
        {
            bopy::throw_error_already_set();
        }
        from_py<tangoTypeConst>::convert(native_obj, *ptr);
        Py_DECREF(native_obj);

        data->convertible = storage;
    }
};

template <long tangoTypeConst>
struct convert_numpy_to_float
{
    typedef typename TANGO_const2type(tangoTypeConst) TangoScalarType;
    static const long NumpyType = TANGO_const2numpy(tangoTypeConst);

    convert_numpy_to_float()
    {
        bopy::converter::registry::push_back(&convertible, &construct, bopy::type_id<TangoScalarType>());
    }

    static void *convertible(PyObject *obj)
    {
        if(!PyArray_CheckScalar(obj))
        {
            return 0;
        }

        PyArray_Descr *type = PyArray_DescrFromScalar(obj);
        if(PyDataType_ISINTEGER(type) || PyDataType_ISFLOAT(type))
        {
            return obj;
        }
        return 0;
    }

    static void construct(PyObject *obj, bopy::converter::rvalue_from_python_stage1_data *data)
    {
        typedef bopy::converter::rvalue_from_python_storage<TangoScalarType> tango_storage;
        void *const storage = reinterpret_cast<tango_storage *>(data)->storage.bytes;
        TangoScalarType *ptr = new(storage) TangoScalarType();

        PyObject *native_obj = PyObject_CallMethod(obj, const_cast<char *>("__float__"), NULL);
        if(native_obj == NULL)
        {
            bopy::throw_error_already_set();
        }
        from_py<tangoTypeConst>::convert(native_obj, *ptr);
        Py_DECREF(native_obj);

        data->convertible = storage;
    }
};
