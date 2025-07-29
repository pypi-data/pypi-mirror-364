/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "pytgutils.h"
#include "callback.h"
#include "device_attribute.h"
#include "exception.h"
#include "device_pipe.h"

struct PyCmdDoneEvent
{
    bopy::object device;
    bopy::object cmd_name;
    bopy::object argout;
    bopy::object argout_raw;
    bopy::object err;
    bopy::object errors;
    bopy::object ext;
};

struct PyAttrReadEvent
{
    bopy::object device;
    bopy::object attr_names;
    bopy::object argout;
    bopy::object err;
    bopy::object errors;
    bopy::object ext;
};

struct PyAttrWrittenEvent
{
    bopy::object device;
    bopy::object attr_names;
    bopy::object err;
    bopy::object errors;
    bopy::object ext;
};

static void copy_most_fields(PyCallBackAutoDie *_self, const Tango::CmdDoneEvent *ev, PyCmdDoneEvent *py_ev)
{
    // py_ev->device
    py_ev->cmd_name = bopy::object(ev->cmd_name);
    py_ev->argout_raw = bopy::object(ev->argout);
    py_ev->err = bopy::object(ev->err);
    py_ev->errors = bopy::object(ev->errors);
    // py_ev->ext =        bopy::object(ev->ext);
}

static void copy_most_fields(PyCallBackAutoDie *_self, const Tango::AttrReadEvent *ev, PyAttrReadEvent *py_ev)
{
    // py_ev->device
    py_ev->attr_names = bopy::object(ev->attr_names);

    PyDeviceAttribute::AutoDevAttrVector dev_attr_vec(ev->argout);
    py_ev->argout = PyDeviceAttribute::convert_to_python(dev_attr_vec, *ev->device, _self->m_extract_as);

    py_ev->err = bopy::object(ev->err);
    py_ev->errors = bopy::object(ev->errors);
    // py_ev->ext = bopy::object(ev->ext);
}

static void copy_most_fields(PyCallBackAutoDie *_self, const Tango::AttrWrittenEvent *ev, PyAttrWrittenEvent *py_ev)
{
    // py_ev->device
    py_ev->attr_names = bopy::object(ev->attr_names);
    py_ev->err = bopy::object(ev->err);
    py_ev->errors = bopy::object(ev->errors);
    // py_ev->ext =        bopy::object(ev->ext);
}

/*static*/ bopy::object PyCallBackAutoDie::py_on_callback_parent_fades;
/*static*/ std::map<PyObject *, PyObject *> PyCallBackAutoDie::s_weak2ob;

PyCallBackAutoDie::~PyCallBackAutoDie()
{
    if(this->m_weak_parent)
    {
        PyCallBackAutoDie::s_weak2ob.erase(this->m_weak_parent);
        bopy::xdecref(this->m_weak_parent);
    }
}

/*static*/ void PyCallBackAutoDie::init()
{
    bopy::object py_scope = bopy::scope();

    bopy::def("__on_callback_parent_fades", on_callback_parent_fades);
    PyCallBackAutoDie::py_on_callback_parent_fades = py_scope.attr("__on_callback_parent_fades");
}

void PyCallBackAutoDie::on_callback_parent_fades(PyObject *weakobj)
{
    PyObject *ob = PyCallBackAutoDie::s_weak2ob[weakobj];

    if(!ob)
    {
        return;
    }

    //     while (ob->ob_refcnt)
    bopy::xdecref(ob);
}

void PyCallBackAutoDie::set_autokill_references(bopy::object &py_self, bopy::object &py_parent)
{
    if(m_self == 0)
    {
        m_self = py_self.ptr();
    }

    assert(m_self == py_self.ptr());

    PyObject *recb = PyCallBackAutoDie::py_on_callback_parent_fades.ptr();
    this->m_weak_parent = PyWeakref_NewRef(py_parent.ptr(), recb);

    if(!this->m_weak_parent)
    {
        bopy::throw_error_already_set();
    }

    bopy::incref(this->m_self);
    PyCallBackAutoDie::s_weak2ob[this->m_weak_parent] = py_self.ptr();
}

void PyCallBackAutoDie::unset_autokill_references()
{
    bopy::decref(m_self);
}

template <typename OriginalT, typename CopyT>
static void _run_virtual_once(PyCallBackAutoDie *_self, OriginalT *ev, const char *virt_fn_name)
{
    AutoPythonGIL gil;

    try
    {
        CopyT *py_ev = new CopyT();
        bopy::object py_value =
            bopy::object(bopy::handle<>(bopy::to_python_indirect<CopyT *, bopy::detail::make_owning_holder>()(py_ev)));

        // - py_ev->device = bopy::object(ev->device); No, we use m_weak_parent
        // so we get exactly the same python bopy::object...
        if(_self->m_weak_parent)
        {
            PyObject *parent = PyWeakref_GET_OBJECT(_self->m_weak_parent);
            if(parent && parent != Py_None)
            {
                py_ev->device = bopy::object(bopy::handle<>(bopy::borrowed(parent)));
            }
        }

        copy_most_fields(_self, ev, py_ev);

        _self->get_override(virt_fn_name)(py_value);
    }
    SAFE_CATCH_INFORM(virt_fn_name)
    _self->unset_autokill_references();
}

/*virtual*/ void PyCallBackAutoDie::cmd_ended(Tango::CmdDoneEvent *ev)
{
    _run_virtual_once<Tango::CmdDoneEvent, PyCmdDoneEvent>(this, ev, "cmd_ended");
}

/*virtual*/ void PyCallBackAutoDie::attr_read(Tango::AttrReadEvent *ev)
{
    _run_virtual_once<Tango::AttrReadEvent, PyAttrReadEvent>(this, ev, "attr_read");
}

/*virtual*/ void PyCallBackAutoDie::attr_written(Tango::AttrWrittenEvent *ev)
{
    _run_virtual_once<Tango::AttrWrittenEvent, PyAttrWrittenEvent>(this, ev, "attr_written");
}

PyCallBackPushEvent::~PyCallBackPushEvent()
{
    bopy::xdecref(this->m_weak_device);
}

void PyCallBackPushEvent::set_device(bopy::object &py_device)
{
    this->m_weak_device = PyWeakref_NewRef(py_device.ptr(), 0);

    if(!this->m_weak_device)
    {
        bopy::throw_error_already_set();
    }
}

namespace
{

template <typename OriginalT>
void copy_device(OriginalT *ev, bopy::object py_ev, bopy::object py_device)
{
    if(py_device.ptr() != Py_None)
    {
        py_ev.attr("device") = py_device;
    }
    else
    {
        py_ev.attr("device") = bopy::object(ev->device);
    }
}

template <typename OriginalT>
static void _push_event(PyCallBackPushEvent *self, OriginalT *ev)
{
    // If the event is received after python dies but before the process
    // finishes then discard the event
    if(!Py_IsInitialized())
    {
        TANGO_LOG_DEBUG << "Tango event (" << ev->event << ") received for after python shutdown. "
                        << "Event will be ignored" << std::endl;
        return;
    }

    AutoPythonGIL gil;

    // Make a copy of ev in python
    // (the original will be deleted by TangoC++ on return)
    bopy::object py_ev(ev);
    OriginalT *ev_copy = bopy::extract<OriginalT *>(py_ev);

    // If possible, reuse the original DeviceProxy
    bopy::object py_device;
    if(self->m_weak_device)
    {
        PyObject *py_c_device = PyWeakref_GET_OBJECT(self->m_weak_device);
        if(py_c_device && py_c_device != Py_None)
        {
            py_device = bopy::object(bopy::handle<>(bopy::borrowed(py_c_device)));
        }
    }

    try
    {
        PyCallBackPushEvent::fill_py_event(ev_copy, py_ev, py_device, self->m_extract_as);
    }
    SAFE_CATCH_REPORT("PyCallBackPushEvent::fill_py_event")

    try
    {
        self->get_override("push_event")(py_ev);
    }
    SAFE_CATCH_INFORM("push_event")
}
} // namespace

bopy::object PyCallBackPushEvent::get_override(const char *name)
{
    return bopy::wrapper<Tango::CallBack>::get_override(name);
}

void PyCallBackPushEvent::fill_py_event(Tango::EventData *ev,
                                        bopy::object &py_ev,
                                        bopy::object py_device,
                                        PyTango::ExtractAs extract_as)
{
    copy_device(ev, py_ev, py_device);
    /// @todo on error extracting, we could save the error in DeviceData
    /// instead of throwing it...?
    // Save a copy of attr_value, so we can still access it after
    // the execution of the callback (Tango will delete the original!)
    // I originally was 'stealing' the reference to TangoC++: I got
    // attr_value and set it to 0... But now TangoC++ is not deleting
    // attr_value pointer but its own copy, so my efforts are useless.
    if(ev->attr_value)
    {
        Tango::DeviceAttribute *attr = new Tango::DeviceAttribute;
        (*attr) = std::move(*ev->attr_value);
        py_ev.attr("attr_value") = PyDeviceAttribute::convert_to_python(attr, *ev->device, extract_as);
    }
    // ev->attr_value = 0; // Do not delete, python will.
}

void PyCallBackPushEvent::fill_py_event(Tango::AttrConfEventData *ev,
                                        bopy::object &py_ev,
                                        bopy::object py_device,
                                        PyTango::ExtractAs extract_as)
{
    copy_device(ev, py_ev, py_device);

    if(ev->attr_conf)
    {
        py_ev.attr("attr_conf") = *ev->attr_conf;
    }
}

void PyCallBackPushEvent::fill_py_event(Tango::DataReadyEventData *ev,
                                        bopy::object &py_ev,
                                        bopy::object py_device,
                                        PyTango::ExtractAs extract_as)
{
    copy_device(ev, py_ev, py_device);
}

void PyCallBackPushEvent::fill_py_event(Tango::PipeEventData *ev,
                                        bopy::object &py_ev,
                                        bopy::object py_device,
                                        PyTango::ExtractAs extract_as)
{
    copy_device(ev, py_ev, py_device);
    if(ev->pipe_value)
    {
        Tango::DevicePipe *pipe_value = new Tango::DevicePipe;
        (*pipe_value) = std::move(*ev->pipe_value);
        py_ev.attr("pipe_value") = PyTango::DevicePipe::convert_to_python(pipe_value, extract_as);
    }
}

void PyCallBackPushEvent::fill_py_event(Tango::DevIntrChangeEventData *ev,
                                        bopy::object &py_ev,
                                        bopy::object py_device,
                                        PyTango::ExtractAs extract_as)
{
    copy_device(ev, py_ev, py_device);

    py_ev.attr("cmd_list") = ev->cmd_list;
    py_ev.attr("att_list") = ev->att_list;
}

/*virtual*/ void PyCallBackPushEvent::push_event(Tango::EventData *ev)
{
    _push_event(this, ev);
}

/*virtual*/ void PyCallBackPushEvent::push_event(Tango::AttrConfEventData *ev)
{
    _push_event(this, ev);
}

/*virtual*/ void PyCallBackPushEvent::push_event(Tango::DataReadyEventData *ev)
{
    _push_event(this, ev);
}

/*virtual*/ void PyCallBackPushEvent::push_event(Tango::PipeEventData *ev)
{
    _push_event(this, ev);
}

/*virtual*/ void PyCallBackPushEvent::push_event(Tango::DevIntrChangeEventData *ev)
{
    _push_event(this, ev);
}

void export_callback()
{
    PyCallBackAutoDie::init();

    /// @todo move somewhere else, another file i tal...

    bopy::class_<PyCmdDoneEvent> CmdDoneEvent("CmdDoneEvent", bopy::no_init);
    CmdDoneEvent.def_readonly("device", &PyCmdDoneEvent::device)
        .def_readonly("cmd_name", &PyCmdDoneEvent::cmd_name)
        .def_readonly("argout_raw", &PyCmdDoneEvent::argout_raw)
        .def_readonly("err", &PyCmdDoneEvent::err)
        .def_readonly("errors", &PyCmdDoneEvent::errors)
        .def_readonly("ext", &PyCmdDoneEvent::ext)
        .def_readwrite("argout", &PyCmdDoneEvent::argout);

    bopy::class_<PyAttrReadEvent> AttrReadEvent("AttrReadEvent", bopy::no_init);
    AttrReadEvent.def_readonly("device", &PyAttrReadEvent::device)
        .def_readonly("attr_names", &PyAttrReadEvent::attr_names)
        .def_readonly("argout", &PyAttrReadEvent::argout)
        .def_readonly("err", &PyAttrReadEvent::err)
        .def_readonly("errors", &PyAttrReadEvent::errors)
        .def_readonly("ext", &PyAttrReadEvent::ext);

    bopy::class_<PyAttrWrittenEvent> AttrWrittenEvent("AttrWrittenEvent", bopy::no_init);
    AttrWrittenEvent.def_readonly("device", &PyAttrWrittenEvent::device)
        .def_readonly("attr_names", &PyAttrWrittenEvent::attr_names)
        .def_readonly("err", &PyAttrWrittenEvent::err)
        .def_readonly("errors", &PyAttrWrittenEvent::errors)
        .def_readonly("ext", &PyAttrWrittenEvent::ext);

    bopy::class_<PyCallBackAutoDie, boost::noncopyable> CallBackAutoDie(
        "__CallBackAutoDie", "INTERNAL CLASS - DO NOT USE IT", bopy::init<>());

    CallBackAutoDie
        .def("cmd_ended",
             &PyCallBackAutoDie::cmd_ended,
             "This method is defined as being empty and must be overloaded by the user when the asynchronous callback "
             "model is used. This is the method which will be executed when the server reply from a command_inout is "
             "received in both push and pull sub-mode.")
        .def("attr_read",
             &PyCallBackAutoDie::attr_read,
             "This method is defined as being empty and must be overloaded by the user when the asynchronous callback "
             "model is used. This is the method which will be executed when the server reply from a read_attribute(s) "
             "is received in both push and pull sub-mode.")
        .def("attr_written",
             &PyCallBackAutoDie::attr_written,
             "This method is defined as being empty and must be overloaded by the user when the asynchronous callback "
             "model is used. This is the method which will be executed when the server reply from a write_attribute(s) "
             "is received in both push and pull sub-mode. ");

    bopy::class_<PyCallBackPushEvent, boost::noncopyable> CallBackPushEvent(
        "__CallBackPushEvent", "INTERNAL CLASS - DO NOT USE IT", bopy::init<>());

    CallBackPushEvent
        .def("push_event",
             (void(PyCallBackAutoDie::*)(Tango::EventData *)) & PyCallBackAutoDie::push_event,
             "This method is defined as being empty and must be overloaded by the user when events are used. This is "
             "the method which will be executed when the server send event(s) to the client. ")
        .def("push_event",
             (void(PyCallBackAutoDie::*)(Tango::AttrConfEventData *)) & PyCallBackAutoDie::push_event,
             "This method is defined as being empty and must be overloaded by the user when events are used. This is "
             "the method which will be executed when the server send attribute configuration change event(s) to the "
             "client. ")
        .def("push_event",
             (void(PyCallBackAutoDie::*)(Tango::DataReadyEventData *)) & PyCallBackAutoDie::push_event,
             "This method is defined as being empty and must be overloaded by the user when events are used. This is "
             "the method which will be executed when the server send attribute data ready event(s) to the client. ")
        .def("push_event",
             (void(PyCallBackAutoDie::*)(Tango::PipeEventData *)) & PyCallBackAutoDie::push_event,
             "This method is defined as being empty and must be overloaded by the user when events are used. This is "
             "the method which will be executed when the server send pipe event(s) to the client. ")
        .def("push_event",
             (void(PyCallBackAutoDie::*)(Tango::DevIntrChangeEventData *)) & PyCallBackAutoDie::push_event,
             "This method is defined as being empty and must be overloaded by the user when events are used. This is "
             "the method which will be executed when the server send device interface change event(s) to the client. ");
}
