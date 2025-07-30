/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "tango_numpy.h"

PyArrayObject *to_PyArrayObject(PyObject *obj)
{
    if(PyArray_Check(obj))
    {
        return (PyArrayObject *) (obj);
    }
    else
    {
        throw std::runtime_error("PyObject is not a numpy array");
    }
}
