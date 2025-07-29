/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "pytgutils.h"
#include "exception.h"

// Useful constants for exceptions

const char *param_must_be_seq = "Parameter must be a string or a python "
                                "sequence (e.x.: a tuple or a list)";

const char *unreachable_code = "Code should be unreachable";

const char *non_string_seq = "Parameter must be a non string sequence "
                             "(e.x.: a tuple or a list)";

const char *non_valid_image = "Parameter must be an IMAGE. This is a sequence"
                              " of sequences (with all the sub-sequences having"
                              " the same length) or a bidimensional numpy.array";

const char *non_valid_spectrum = "Parameter must be an SPECTRUM. This is a"
                                 " sequence of scalar values or a unidimensional"
                                 " numpy.array";

bopy::object PyTango_DevFailed, PyTango_ConnectionFailed, PyTango_CommunicationFailed, PyTango_WrongNameSyntax,
    PyTango_NonDbDevice, PyTango_WrongData, PyTango_NonSupportedFeature, PyTango_AsynCall, PyTango_AsynReplyNotArrived,
    PyTango_EventSystemFailed, PyTango_DeviceUnlocked, PyTango_NotAllowed;

namespace Tango
{
inline bool operator==(const Tango::NamedDevFailed &df1, const Tango::NamedDevFailed &df2)
{
    /// @todo ? err_stack ?
    return (df1.name == df2.name) && (df1.idx_in_call == df2.idx_in_call);
}
} // namespace Tango

void sequencePyDevError_2_DevErrorList(PyObject *value, Tango::DevErrorList &del)
{
    long len = (std::max)((int) PySequence_Size(value), 0);
    del.length(len);

    for(long loop = 0; loop < len; ++loop)
    {
        PyObject *item = PySequence_GetItem(value, loop);
        Tango::DevError &dev_error = bopy::extract<Tango::DevError &>(item);
        del[loop].desc = CORBA::string_dup(dev_error.desc);
        del[loop].reason = CORBA::string_dup(dev_error.reason);
        del[loop].origin = CORBA::string_dup(dev_error.origin);
        del[loop].severity = dev_error.severity;
        Py_XDECREF(item);
    }
}

void PyDevFailed_2_DevFailed(PyObject *value, Tango::DevFailed &df)
{
    if(PyObject_IsInstance(value, PyTango_DevFailed.ptr()))
    {
        PyObject *args = PyObject_GetAttrString(value, "args");
        if(PySequence_Check(args) == 0)
        {
            Py_XDECREF(args);

            Tango::Except::throw_exception((const char *) "PyDs_BadDevFailedException",
                                           (const char *) "A badly formed exception has been received",
                                           (const char *) "PyDevFailed_2_DevFailed");
        }
        else
        {
            sequencePyDevError_2_DevErrorList(args, df.errors);
            Py_DECREF(args);
        }
    }
    else
    {
        sequencePyDevError_2_DevErrorList(value, df.errors);
    }
}

void throw_python_dev_failed()
{
    PyObject *type, *value, *traceback;
    PyErr_Fetch(&type, &value, &traceback);

    if(value == NULL)
    {
        Py_XDECREF(type);
        Py_XDECREF(traceback);

        Tango::Except::throw_exception((const char *) "PyDs_BadDevFailedException",
                                       (const char *) "A badly formed exception has been received",
                                       (const char *) "throw_python_dev_failed");
    }

    Tango::DevFailed df;
    try
    {
        PyDevFailed_2_DevFailed(value, df);
    }
    catch(...)
    {
        Py_XDECREF(type);
        Py_XDECREF(value);
        Py_XDECREF(traceback);
        throw;
    }

    Py_XDECREF(type);
    Py_XDECREF(value);
    Py_XDECREF(traceback);

    throw df;
}

Tango::DevFailed to_dev_failed(PyObject *type, PyObject *value, PyObject *traceback)
{
    bool from_fetch = false;
    if((type == NULL) || (value == NULL) || (traceback == NULL) || (type == Py_None) || (value == Py_None) ||
       (traceback == Py_None))
    {
        PyErr_Fetch(&type, &value, &traceback);
        PyErr_NormalizeException(&type, &value, &traceback);
        from_fetch = true;
    }

    Tango::DevErrorList dev_err;
    dev_err.length(1);

    if(value == NULL)
    {
        //
        // Send a default exception in case Python does not send us information
        //
        dev_err[0].origin = CORBA::string_dup("Py_to_dev_failed");
        dev_err[0].desc = CORBA::string_dup("A badly formed exception has been received");
        dev_err[0].reason = CORBA::string_dup("PyDs_BadPythonException");
        dev_err[0].severity = Tango::ERR;
    }
    else
    {
        //
        // Populate a one level DevFailed exception
        //

        PyObject *tracebackModule = PyImport_ImportModule("traceback");
        if(tracebackModule != NULL)
        {
            //
            // Format the traceback part of the Python exception
            // and store it in the origin part of the Tango exception
            //

            PyObject *tbList_ptr = PyObject_CallMethod(
                tracebackModule, (char *) "format_exception", (char *) "OOO", type, value, traceback);

            try
            {
                bopy::object tbList = bopy::object(bopy::handle<>(tbList_ptr));
                bopy::str origin = bopy::str("").join(tbList);
                char const *origin_ptr = bopy::extract<char const *>(origin);
                dev_err[0].origin = CORBA::string_dup(origin_ptr);
            }
            catch(...)
            {
                dev_err[0].origin = CORBA::string_dup("UNKNOWN: cannot get Python's traceback. "
                                                      "Most probably, was a failure in c++ bindings");
            }

            //
            // Format the exec and value part of the Python exception
            // and store it in the desc part of the Tango exception
            //

            tbList_ptr = PyObject_CallMethod(tracebackModule,
                                             (char *) "format_exception_only",
                                             (char *) "OO",
                                             type,
                                             value == NULL ? Py_None : value);

            bopy::object tbList = bopy::object(bopy::handle<>(tbList_ptr));
            bopy::str desc = bopy::str("").join(tbList);
            char const *desc_ptr = bopy::extract<char const *>(desc);
            dev_err[0].desc = CORBA::string_dup(desc_ptr);

            Py_DECREF(tracebackModule);

            dev_err[0].reason = CORBA::string_dup("PyDs_PythonError");
            dev_err[0].severity = Tango::ERR;
        }
        else
        {
            //
            // Send a default exception because we can't format the
            // different parts of the Python's one !
            //

            dev_err[0].origin = CORBA::string_dup("Py_to_dev_failed");
            dev_err[0].desc =
                CORBA::string_dup("Can't import Python traceback module. Can't extract info from Python exception");
            dev_err[0].reason = CORBA::string_dup("PyDs_PythonError");
            dev_err[0].severity = Tango::ERR;
        }
    }
    if(from_fetch)
    {
        Py_XDECREF(type);
        Py_XDECREF(value);
        Py_XDECREF(traceback);
    }
    return Tango::DevFailed(dev_err);
}

void throw_python_generic_exception(PyObject *type, PyObject *value, PyObject *traceback)
{
    throw to_dev_failed(type, value, traceback);
}

void handle_python_exception(bopy::error_already_set &eas,
                             const std::string &reason,
                             const std::string &desc,
                             const std::string &origin)
{
    if(PyErr_ExceptionMatches(PyTango_DevFailed.ptr()))
    {
        throw_python_dev_failed();
    }
    else
    {
        Tango::DevFailed dev_err = to_dev_failed();
        if(origin != "" || desc != "" || reason != "")
        {
            long nb_err = dev_err.errors.length();
            dev_err.errors.length(nb_err + 1);
            dev_err.errors[nb_err].reason = CORBA::string_dup(reason.c_str());
            dev_err.errors[nb_err].desc = CORBA::string_dup(desc.c_str());
            dev_err.errors[nb_err].origin = CORBA::string_dup(origin.c_str());
            dev_err.errors[nb_err].severity = Tango::ERR;
        }
        throw dev_err;
    }
}

struct convert_PyDevFailed_to_DevFailed
{
    convert_PyDevFailed_to_DevFailed()
    {
        bopy::converter::registry::push_back(&convertible, &construct, bopy::type_id<Tango::DevFailed>());
    }

    // Check if given Python object is convertible to a DevFailed.
    // If so, return obj, otherwise return 0
    static void *convertible(PyObject *obj)
    {
        if(PyObject_IsInstance(obj, PyTango_DevFailed.ptr()))
        {
            return obj;
        }

        return 0;
    }

    // Construct a vec3f object from the given Python object, and
    // store it in the stage1 (?) data.
    static void construct(PyObject *obj, bopy::converter::rvalue_from_python_stage1_data *data)
    {
        typedef bopy::converter::rvalue_from_python_storage<Tango::DevFailed> DevFailed_storage;

        void *const storage = reinterpret_cast<DevFailed_storage *>(data)->storage.bytes;

        Tango::DevFailed *df_ptr = new(storage) Tango::DevFailed();
        PyDevFailed_2_DevFailed(obj, *df_ptr);
        data->convertible = storage;
    }
};

void _translate_dev_failed(const Tango::DevFailed &dev_failed, bopy::object py_dev_failed)
{
    bopy::object py_errors(dev_failed.errors);
    PyErr_SetObject(py_dev_failed.ptr(), py_errors.ptr());
}

void translate_dev_failed(const Tango::DevFailed &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_DevFailed);
}

void translate_connection_failed(const Tango::ConnectionFailed &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_ConnectionFailed);
}

void translate_communication_failed(const Tango::CommunicationFailed &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_CommunicationFailed);
}

void translate_wrong_name_syntax(const Tango::WrongNameSyntax &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_WrongNameSyntax);
}

void translate_non_db_device(const Tango::NonDbDevice &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_NonDbDevice);
}

void translate_wrong_data(const Tango::WrongData &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_WrongData);
}

void translate_non_supported_feature(const Tango::NonSupportedFeature &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_NonSupportedFeature);
}

void translate_asyn_call(const Tango::AsynCall &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_AsynCall);
}

void translate_asyn_reply_not_arrived(const Tango::AsynReplyNotArrived &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_AsynReplyNotArrived);
}

void translate_event_system_failed(const Tango::EventSystemFailed &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_EventSystemFailed);
}

void translate_device_unlocked(const Tango::DeviceUnlocked &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_DeviceUnlocked);
}

void translate_not_allowed(const Tango::NotAllowed &dev_failed)
{
    _translate_dev_failed(dev_failed, PyTango_NotAllowed);
}

namespace PyExcept
{
inline void throw_exception(const char *a, const char *b, const char *c)
{
    Tango::Except::throw_exception(a, b, c);
}

inline void throw_exception_severity(const char *a, const char *b, const char *c, Tango::ErrSeverity d)
{
    Tango::Except::throw_exception(a, b, c, d);
}

inline void re_throw_exception(const Tango::DevFailed &df, const char *a, const char *b, const char *c)
{
    Tango::Except::re_throw_exception(const_cast<Tango::DevFailed &>(df), a, b, c);
}

inline void re_throw_exception_severity(
    const Tango::DevFailed &df, const char *a, const char *b, const char *c, Tango::ErrSeverity d)
{
    Tango::Except::re_throw_exception(const_cast<Tango::DevFailed &>(df), a, b, c, d);
}

inline void print_exception(const Tango::DevFailed &df)
{
    Tango::Except::print_exception(df);
}
} // namespace PyExcept

namespace PyNamedDevFailed
{
Tango::DevErrorList get_err_stack(Tango::NamedDevFailed &self)
{
    return self.err_stack;
}
} // namespace PyNamedDevFailed

BOOST_PYTHON_FUNCTION_OVERLOADS(to_dev_failed_overloads, to_dev_failed, 0, 3)
BOOST_PYTHON_FUNCTION_OVERLOADS(throw_python_generic_exception_overloads, throw_python_generic_exception, 0, 3)

void export_exceptions()
{
    bool (*compare_exception_)(Tango::DevFailed &, Tango::DevFailed &) = &Tango::Except::compare_exception;

    PyTango_DevFailed = bopy::object(bopy::handle<>(PyErr_NewException((char *) "PyTango.DevFailed", NULL, NULL)));

    PyObject *df_ptr = PyTango_DevFailed.ptr();

    PyTango_ConnectionFailed =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.ConnectionFailed"), df_ptr, NULL)));
    PyTango_CommunicationFailed = bopy::object(
        bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.CommunicationFailed"), df_ptr, NULL)));
    PyTango_WrongNameSyntax =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.WrongNameSyntax"), df_ptr, NULL)));
    PyTango_NonDbDevice =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.NonDbDevice"), df_ptr, NULL)));
    PyTango_WrongData =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.WrongData"), df_ptr, NULL)));
    PyTango_NonSupportedFeature = bopy::object(
        bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.NonSupportedFeature"), df_ptr, NULL)));
    PyTango_AsynCall =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.AsynCall"), df_ptr, NULL)));
    PyTango_AsynReplyNotArrived = bopy::object(
        bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.AsynReplyNotArrived"), df_ptr, NULL)));
    PyTango_EventSystemFailed =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.EventSystemFailed"), df_ptr, NULL)));
    PyTango_DeviceUnlocked =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.DeviceUnlocked"), df_ptr, NULL)));
    PyTango_NotAllowed =
        bopy::object(bopy::handle<>(PyErr_NewException(const_cast<char *>("PyTango.NotAllowed"), df_ptr, NULL)));

    bopy::scope().attr("DevFailed") = PyTango_DevFailed;
    bopy::scope().attr("ConnectionFailed") = PyTango_ConnectionFailed;
    bopy::scope().attr("CommunicationFailed") = PyTango_CommunicationFailed;
    bopy::scope().attr("WrongNameSyntax") = PyTango_WrongNameSyntax;
    bopy::scope().attr("NonDbDevice") = PyTango_NonDbDevice;
    bopy::scope().attr("WrongData") = PyTango_WrongData;
    bopy::scope().attr("NonSupportedFeature") = PyTango_NonSupportedFeature;
    bopy::scope().attr("AsynCall") = PyTango_AsynCall;
    bopy::scope().attr("AsynReplyNotArrived") = PyTango_AsynReplyNotArrived;
    bopy::scope().attr("EventSystemFailed") = PyTango_EventSystemFailed;
    bopy::scope().attr("DeviceUnlocked") = PyTango_DeviceUnlocked;
    bopy::scope().attr("NotAllowed") = PyTango_NotAllowed;

    bopy::register_exception_translator<Tango::DevFailed>(&translate_dev_failed);
    bopy::register_exception_translator<Tango::ConnectionFailed>(&translate_connection_failed);
    bopy::register_exception_translator<Tango::CommunicationFailed>(&translate_communication_failed);
    bopy::register_exception_translator<Tango::WrongNameSyntax>(&translate_wrong_name_syntax);
    bopy::register_exception_translator<Tango::NonDbDevice>(&translate_non_db_device);
    bopy::register_exception_translator<Tango::WrongData>(&translate_wrong_data);
    bopy::register_exception_translator<Tango::NonSupportedFeature>(&translate_non_supported_feature);
    bopy::register_exception_translator<Tango::AsynCall>(&translate_asyn_call);
    bopy::register_exception_translator<Tango::AsynReplyNotArrived>(&translate_asyn_reply_not_arrived);
    bopy::register_exception_translator<Tango::EventSystemFailed>(&translate_event_system_failed);
    bopy::register_exception_translator<Tango::DeviceUnlocked>(&translate_device_unlocked);
    bopy::register_exception_translator<Tango::NotAllowed>(&translate_not_allowed);

    bopy::class_<Tango::Except, boost::noncopyable>("Except", bopy::no_init)
        .def("throw_exception", &PyExcept::throw_exception)
        .def("throw_exception", &PyExcept::throw_exception_severity)
        .def("re_throw_exception", &PyExcept::re_throw_exception)
        .def("re_throw_exception", &PyExcept::re_throw_exception_severity)
        .def("print_exception", &PyExcept::print_exception)
        .def("print_error_stack", (void (*)(const Tango::DevErrorList &)) & Tango::Except::print_error_stack)
        .def("compare_exception", (bool (*)(const Tango::DevFailed &, const Tango::DevFailed &)) compare_exception_)
        .def("to_dev_failed", &to_dev_failed, to_dev_failed_overloads())
        .def("throw_python_exception", &throw_python_generic_exception, throw_python_generic_exception_overloads())
        .staticmethod("throw_exception")
        .staticmethod("re_throw_exception")
        .staticmethod("print_exception")
        .staticmethod("print_error_stack")
        .staticmethod("to_dev_failed")
        .staticmethod("throw_python_exception");

    convert_PyDevFailed_to_DevFailed pydevfailed_2_devfailed;

    /// NamedDevFailed & family:
    bopy::class_<Tango::NamedDevFailed> NamedDevFailed("NamedDevFailed", "", bopy::no_init);

    NamedDevFailed
        .def_readonly("name", &Tango::NamedDevFailed::name)               // string
        .def_readonly("idx_in_call", &Tango::NamedDevFailed::idx_in_call) // long
        .add_property("err_stack", PyNamedDevFailed::get_err_stack)       // DevErrorList
        ;

    typedef std::vector<Tango::NamedDevFailed> StdNamedDevFailedVector_;
    bopy::class_<StdNamedDevFailedVector_>("StdNamedDevFailedVector")
        .def(bopy::vector_indexing_suite<StdNamedDevFailedVector_>());

    // DevFailed is not really exported but just translated, so we can't
    // derivate.
    bopy::class_<Tango::NamedDevFailedList /*, bases<Tango::DevFailed>*/> NamedDevFailedList(
        "NamedDevFailedList", "", bopy::no_init);

    NamedDevFailedList
        .def("get_faulty_attr_nb", &Tango::NamedDevFailedList::get_faulty_attr_nb) // size_t
        .def("call_failed", &Tango::NamedDevFailedList::call_failed)               // bool
        .def_readonly("err_list", &Tango::NamedDevFailedList::err_list)            // std::vector<NamedDevFailed>
        ;
}
