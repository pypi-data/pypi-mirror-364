/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#pragma once

#include <Python.h>

// See "Importing the API" for the why of these weird defines before
// the inclusion of numpy. They are needed so that you can do import_array
// in just one file while using numpy in all the project files.
// http://docs.scipy.org/doc/numpy/reference/c-api.array.html#miscellaneous
// - {
#define PY_ARRAY_UNIQUE_SYMBOL pytango_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>
// - }

#include "tgutils.h"

/// @name Conversion from a Tango scalar type name to the numpy equivalent name
/// @{

#define TANGO_const2numpy(tangoid) tango_name2numpy<tangoid>::value

template <int N>
struct tango_name2numpy
{
    enum e_tango_name2numpy
    {
    };
};

#define DEF_TANGO2NUMPY(tangoid, numpyid) \
    template <>                           \
    struct tango_name2numpy<tangoid>      \
    {                                     \
        enum e_tango_name2numpy           \
        {                                 \
            value = numpyid               \
        };                                \
    }

DEF_TANGO2NUMPY(Tango::DEV_STATE, NPY_UINT32);
DEF_TANGO2NUMPY(Tango::DEV_SHORT, NPY_INT16);
DEF_TANGO2NUMPY(Tango::DEV_LONG, NPY_INT32);
DEF_TANGO2NUMPY(Tango::DEV_DOUBLE, NPY_FLOAT64);
DEF_TANGO2NUMPY(Tango::DEV_FLOAT, NPY_FLOAT32);
DEF_TANGO2NUMPY(Tango::DEV_BOOLEAN, NPY_BOOL);
DEF_TANGO2NUMPY(Tango::DEV_USHORT, NPY_UINT16);
DEF_TANGO2NUMPY(Tango::DEV_ULONG, NPY_UINT32);
// Unassigned Tango::DEV_STRING, mapping to NPY_STRING is not copy-free
DEF_TANGO2NUMPY(Tango::DEV_UCHAR, NPY_UBYTE);
// DEF_TANGO2NUMPY(Tango::DEV_CHAR, NPY_BYTE );
// Unassigned: Tango::DEV_ENCODED
DEF_TANGO2NUMPY(Tango::DEV_LONG64, NPY_INT64);
DEF_TANGO2NUMPY(Tango::DEV_ULONG64, NPY_UINT64);
DEF_TANGO2NUMPY(Tango::DEV_ENUM, NPY_INT16);

/// @name Conversion from a Tango array type name to the scalar numpy name
/// For types like DEVVAR_DOUBLEARRAY. This is ended with ARRAY, except
/// DEVVAR_LONGSTRINGARRAY, DEVVAR_DOUBLESTRINGARRAY and DEVVAR_STRINGARRAY
/// @{

#define TANGO_const2scalarnumpy(tangoid) tango_name2scalarnumpy<tangoid>::value

// We can use TANGO_const2scalarconst which gives us the equivalence
// except for DEVVAR_CHARARRAY, that does not have any Scalar type
// equivalent.
template <int N>
struct tango_name2scalarnumpy
{
    enum
    {
        value = TANGO_const2numpy(TANGO_const2scalarconst(N))
    };
};

template <>
struct tango_name2scalarnumpy<Tango::DEVVAR_CHARARRAY>
{
    enum
    {
        value = NPY_UBYTE
    };
};

/// @}

// Utility function to cast PyObject to PyArrayObject
// Expects an object to be a numpy array
PyArrayObject *to_PyArrayObject(PyObject *);
