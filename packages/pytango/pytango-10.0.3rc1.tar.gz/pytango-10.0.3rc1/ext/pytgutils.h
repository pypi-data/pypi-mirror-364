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
#include "from_py.h"
#include "to_py.h"
#include "tgutils.h"

/// Get the python Global Interpret Lock
class AutoPythonGIL
{
    PyGILState_STATE m_gstate;

    /**
     * Check python. Before acquiring python GIL check if python as not been
     * shutdown. If this is the case then the best we can do here is throw an
     * exception to try to prevent the PyTango from calling python code
     **/
    inline void check_python()
    {
        if(!Py_IsInitialized())
        {
            Tango::Except::throw_exception("AutoPythonGIL_PythonShutdown",
                                           "Trying to execute python code when python interpreter as shutdown.",
                                           "AutoPythonGIL::check_python");
        }
    }

  public:
    inline AutoPythonGIL(bool safe = true)
    {
        if(safe)
        {
            check_python();
        }
        m_gstate = PyGILState_Ensure();
    }

    inline ~AutoPythonGIL()
    {
        PyGILState_Release(m_gstate);
    }
};

/**
 * Translate a double into a timeval structure
 *
 * @param[out] tv timeval structure to be filled with the time
 * @param[in] t a double representing the time
 */
inline void double2timeval(struct timeval &tv, double t)
{
    double sec = floor(t);
#ifdef WIN32
    tv.tv_usec = (long) ((t - sec) * 1.0E6);
    tv.tv_sec = (long) (sec);
#else
    tv.tv_usec = (time_t) ((t - sec) * 1.0E6);
    tv.tv_sec = (suseconds_t) (sec);
#endif
}
