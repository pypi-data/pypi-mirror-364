/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#ifndef _DEVICE_IMPL_H
#define _DEVICE_IMPL_H

#include <boost/python.hpp>
#include <tango/tango.h>

#include "pytgutils.h"
#include "exception.h"
#include "server/device_class.h"

#define __AUX_DECL_CALL_DEVICE_METHOD AutoPythonGIL __py_lock;

#define __AUX_CATCH_EXCEPTIONS(name)                                                                   \
    catch(bopy::error_already_set & eas)                                                               \
    {                                                                                                  \
        handle_python_exception(eas);                                                                  \
    }                                                                                                  \
    catch(...)                                                                                         \
    {                                                                                                  \
        Tango::Except::throw_exception("CppException", "An unexpected C++ exception occurred", #name); \
    }

#define CALL_DEVICE_METHOD(cls, name)                       \
    __AUX_DECL_CALL_DEVICE_METHOD                           \
    try                                                     \
    {                                                       \
        if(bopy::override name = this->get_override(#name)) \
        {                                                   \
            name();                                         \
        }                                                   \
        else                                                \
        {                                                   \
            cls ::name();                                   \
        }                                                   \
    }                                                       \
    __AUX_CATCH_EXCEPTIONS(name)

#define CALL_DEVICE_METHOD_VARGS(cls, name, ...)            \
    __AUX_DECL_CALL_DEVICE_METHOD                           \
    try                                                     \
    {                                                       \
        if(bopy::override name = this->get_override(#name)) \
        {                                                   \
            name(__VA_ARGS__);                              \
        }                                                   \
        else                                                \
        {                                                   \
            cls ::name(__VA_ARGS__);                        \
        }                                                   \
    }                                                       \
    __AUX_CATCH_EXCEPTIONS(name)

#define CALL_DEVICE_METHOD_RET(cls, name)                   \
    __AUX_DECL_CALL_DEVICE_METHOD                           \
    try                                                     \
    {                                                       \
        if(bopy::override name = this->get_override(#name)) \
        {                                                   \
            return name();                                  \
        }                                                   \
        else                                                \
        {                                                   \
            return cls ::name();                            \
        }                                                   \
    }                                                       \
    __AUX_CATCH_EXCEPTIONS(name)

/**
 * A wrapper around the Tango::DeviceImpl class
 */
class DeviceImplWrap : public Tango::DeviceImpl, public bopy::wrapper<Tango::DeviceImpl>
{
  public:
    /** a reference to itself */
    PyObject *m_self;

    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] st
     */
    DeviceImplWrap(PyObject *self, CppDeviceClass *cl, std::string &st);

    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] name
     * @param[in] desc
     * @param[in] sta
     * @param[in] status
     */
    DeviceImplWrap(PyObject *self,
                   CppDeviceClass *cl,
                   const char *name,
                   const char *desc = "A Tango device",
                   Tango::DevState sta = Tango::UNKNOWN,
                   const char *status = Tango::StatusNotSet);

    /**
     * Destructor
     */
    virtual ~DeviceImplWrap() { }

    /**
     * Invokes the actual init_device
     */
    void init_device();

    bool _is_attribute_polled(const std::string &att_name);
    bool _is_command_polled(const std::string &cmd_name);
    int _get_attribute_poll_period(const std::string &att_name);
    int _get_command_poll_period(const std::string &cmd_name);
    void _poll_attribute(const std::string &att_name, int period);
    void _poll_command(const std::string &cmd_name, int period);
    void _stop_poll_attribute(const std::string &att_name);
    void _stop_poll_command(const std::string &cmd_name);
};

/**
 * A wrapper around the Tango::Device_2Impl class
 */
class Device_2ImplWrap : public Tango::Device_2Impl, public bopy::wrapper<Tango::Device_2Impl>
{
  public:
    /** a reference to itself */
    PyObject *m_self;

    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] st
     */
    Device_2ImplWrap(PyObject *self, CppDeviceClass *cl, std::string &st);

    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] name
     * @param[in] desc
     * @param[in] sta
     * @param[in] status
     */
    Device_2ImplWrap(PyObject *self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet);

    /**
     * Destructor
     */
    virtual ~Device_2ImplWrap() { }

    /**
     * Invokes the actual init_device
     */
    void init_device();
};

class PyDeviceImplBase
{
  public:
    /** a reference to itself */
    PyObject *the_self;

    std::string the_status;

    PyDeviceImplBase(PyObject *self) :
        the_self(self)
    {
        Py_INCREF(the_self);
    }

    virtual ~PyDeviceImplBase() { }

    virtual void py_delete_dev(){};
};

/**
 * A wrapper around the Tango::Device_XImpl class
 */
template <typename TangoDeviceImpl>
class Device_XImplWrap : public TangoDeviceImpl, public PyDeviceImplBase, public bopy::wrapper<TangoDeviceImpl>
{
  public:
    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] st
     */
    Device_XImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
        TangoDeviceImpl(cl, st),
        PyDeviceImplBase(_self)
    {
        _init();
    }

    /**
     * Constructor
     *
     * @param[in] self
     * @param[in] cl
     * @param[in] name
     * @param[in] desc
     * @param[in] sta
     * @param[in] status
     */
    Device_XImplWrap(PyObject *_self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *_desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet) :
        TangoDeviceImpl(cl, name, _desc, sta, status),
        PyDeviceImplBase(_self)
    {
        _init();
    }

    /**
     * Destructor
     */
    virtual ~Device_XImplWrap()
    {
        delete_device();
    }

    /**
     * Necessary init_device implementation to call python
     */
    virtual void init_device()
    {
        AutoPythonGIL __py_lock;
        try
        {
            this->get_override("init_device")();
        }
        catch(bopy::error_already_set &eas)
        {
            handle_python_exception(eas);
        }
    }

    /**
     * Necessary server_init_hook implementation to call python
     */
    virtual void server_init_hook(){CALL_DEVICE_METHOD(TangoDeviceImpl, server_init_hook)};

    /**
     * Executes default server_init_hook implementation
     */
    void default_server_init_hook()
    {
        this->TangoDeviceImpl::server_init_hook();
    }

    /**
     * Necessary delete_device implementation to call python
     */
    virtual void delete_device()
    {
        CALL_DEVICE_METHOD(TangoDeviceImpl, delete_device)
    }

    /**
     * Executes default delete_device implementation
     */
    void default_delete_device()
    {
        this->TangoDeviceImpl::delete_device();
    }

    /**
     * called to ask Python to delete a device by decrementing the Python
     * reference count
     */
    virtual void delete_dev()
    {
        // Call here the delete_device method. It is defined in Device_3ImplWrap
        // class which is already destroyed when the Tango kernel call the
        // delete_device method
        try
        {
            delete_device();
        }
        catch(Tango::DevFailed &e)
        {
            Tango::Except::print_exception(e);
        }
    }

    void py_delete_dev()
    {
        Device_XImplWrap::delete_dev();
        PyDeviceImplBase::py_delete_dev();
    }

    /**
     * Necessary always_executed_hook implementation to call python
     */
    virtual void always_executed_hook(){CALL_DEVICE_METHOD(TangoDeviceImpl, always_executed_hook)};

    /**
     * Executes default always_executed_hook implementation
     */
    void default_always_executed_hook()
    {
        this->TangoDeviceImpl::always_executed_hook();
    }

    /**
     * Necessary read_attr_hardware implementation to call python
     */
    virtual void read_attr_hardware(std::vector<long> &attr_list){
        CALL_DEVICE_METHOD_VARGS(TangoDeviceImpl, read_attr_hardware, attr_list)};

    /**
     * Executes default read_attr_hardware implementation
     */
    void default_read_attr_hardware(std::vector<long> &attr_list)
    {
        this->TangoDeviceImpl::read_attr_hardware(attr_list);
    }

    /**
     * Necessary write_attr_hardware implementation to call python
     */
    virtual void write_attr_hardware(std::vector<long> &attr_list){
        CALL_DEVICE_METHOD_VARGS(TangoDeviceImpl, write_attr_hardware, attr_list)};

    /**
     * Executes default write_attr_hardware implementation
     */
    void default_write_attr_hardware(std::vector<long> &attr_list)
    {
        this->TangoDeviceImpl::write_attr_hardware(attr_list);
    }

    /**
     * Necessary dev_state implementation to call python
     */
    virtual Tango::DevState dev_state()
    {
        CALL_DEVICE_METHOD_RET(TangoDeviceImpl, dev_state)
        // Keep the compiler quiet
        return Tango::UNKNOWN;
    }

    /**
     * Executes default dev_state implementation
     */
    Tango::DevState default_dev_state()
    {
        return this->TangoDeviceImpl::dev_state();
    }

    /**
     * Necessary dev_status implementation to call python
     */
    virtual Tango::ConstDevString dev_status()
    {
        __AUX_DECL_CALL_DEVICE_METHOD
        try
        {
            if(bopy::override dev_status = this->get_override("dev_status"))
            {
                this->the_status = bopy::call<const std::string>(dev_status.ptr());
            }
            else
            {
                this->the_status = TangoDeviceImpl::dev_status();
            }
        }
        __AUX_CATCH_EXCEPTIONS(dev_status)

        return this->the_status.c_str();
    }

    /**
     * Executes default dev_status implementation
     */
    Tango::ConstDevString default_dev_status()
    {
        return this->TangoDeviceImpl::dev_status();
    }

    /**
     * Necessary signal_handler implementation to call python
     */
    virtual void signal_handler(long signo)
    {
        try
        {
            CALL_DEVICE_METHOD_VARGS(TangoDeviceImpl, signal_handler, signo)
        }
        catch(Tango::DevFailed &df)
        {
            long nb_err = df.errors.length();
            df.errors.length(nb_err + 1);

            df.errors[nb_err].reason = CORBA::string_dup("PyDs_UnmanagedSignalHandlerException");
            df.errors[nb_err].desc =
                CORBA::string_dup("An unmanaged Tango::DevFailed exception occurred in signal_handler");

            TangoSys_OMemStream origin;
            origin << TANGO_EXCEPTION_ORIGIN << std::ends;

            df.errors[nb_err].origin = CORBA::string_dup(origin.str().c_str());
            df.errors[nb_err].severity = Tango::ERR;

            Tango::Except::print_exception(df);
        }
    }

    /**
     * Executes default signal_handler implementation
     */
    void default_signal_handler(long signo)
    {
        this->TangoDeviceImpl::signal_handler(signo);
    }

  protected:
    /**
     * internal method used to initialize the class. Called by the constructors
     */
    void _init()
    {
        // Make sure the wrapper contains a valid pointer to the self
        // I found out this is needed by inspecting the boost wrapper_base.hpp code
        initialize_wrapper(the_self, this);
    }
};

/**
 * A wrapper around the Tango::Device_3Impl class
 */
class Device_3ImplWrap : public Device_XImplWrap<Tango::Device_3Impl>
{
  public:
    Device_3ImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
        Device_XImplWrap(_self, cl, st){};

    Device_3ImplWrap(PyObject *_self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *_desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet) :
        Device_XImplWrap(_self, cl, name, _desc, sta, status){};

    /**
     * I do not know why, but boost does link methods from template,
     * so we must have them implemented in wrapper (or I do something wrong)
     * so I just add simplest realization, which just call the parent method
     */

    void default_server_init_hook()
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_server_init_hook();
    }

    void default_delete_device()
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_delete_device();
    }

    void default_always_executed_hook()
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_always_executed_hook();
    }

    void default_read_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_read_attr_hardware(attr_list);
    }

    void default_write_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_write_attr_hardware(attr_list);
    }

    Tango::DevState default_dev_state()
    {
        return Device_XImplWrap<Tango::Device_3Impl>::default_dev_state();
    }

    Tango::ConstDevString default_dev_status()
    {
        return Device_XImplWrap<Tango::Device_3Impl>::default_dev_status();
    }

    void default_signal_handler(long signo)
    {
        Device_XImplWrap<Tango::Device_3Impl>::default_signal_handler(signo);
    }
};

/**
 * A wrapper around the Tango::Device_4Impl class
 */
class Device_4ImplWrap : public Device_XImplWrap<Tango::Device_4Impl>
{
  public:
    Device_4ImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
        Device_XImplWrap(_self, cl, st){};

    Device_4ImplWrap(PyObject *_self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *_desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet) :
        Device_XImplWrap(_self, cl, name, _desc, sta, status){};

    /**
     * I do not know why, but boost does link methods from template,
     * so we must have them implemented in wrapper (or I do something wrong)
     * so I just add simplest realization, which just call the parent method
     */

    void default_server_init_hook()
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_server_init_hook();
    }

    void default_delete_device()
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_delete_device();
    }

    void default_always_executed_hook()
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_always_executed_hook();
    }

    void default_read_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_read_attr_hardware(attr_list);
    }

    void default_write_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_write_attr_hardware(attr_list);
    }

    Tango::DevState default_dev_state()
    {
        return Device_XImplWrap<Tango::Device_4Impl>::default_dev_state();
    }

    Tango::ConstDevString default_dev_status()
    {
        return Device_XImplWrap<Tango::Device_4Impl>::default_dev_status();
    }

    void default_signal_handler(long signo)
    {
        Device_XImplWrap<Tango::Device_4Impl>::default_signal_handler(signo);
    }
};

/**
 * A wrapper around the Tango::Device_5Impl class
 */
class Device_5ImplWrap : public Device_XImplWrap<Tango::Device_5Impl>
{
  public:
    Device_5ImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
        Device_XImplWrap(_self, cl, st){};

    Device_5ImplWrap(PyObject *_self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *_desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet) :
        Device_XImplWrap(_self, cl, name, _desc, sta, status){};

    /**
     * I do not know why, but boost does link methods from template,
     * so we must have them implemented in wrapper (or I do something wrong)
     * so I just add simplest realization, which just call the parent method
     */

    void default_server_init_hook()
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_server_init_hook();
    }

    void default_delete_device()
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_delete_device();
    }

    void default_always_executed_hook()
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_always_executed_hook();
    }

    void default_read_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_read_attr_hardware(attr_list);
    }

    void default_write_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_write_attr_hardware(attr_list);
    }

    Tango::DevState default_dev_state()
    {
        return Device_XImplWrap<Tango::Device_5Impl>::default_dev_state();
    }

    Tango::ConstDevString default_dev_status()
    {
        return Device_XImplWrap<Tango::Device_5Impl>::default_dev_status();
    }

    void default_signal_handler(long signo)
    {
        Device_XImplWrap<Tango::Device_5Impl>::default_signal_handler(signo);
    }
};

/**
 * A wrapper around the Tango::Device_6Impl class
 */
class Device_6ImplWrap : public Device_XImplWrap<Tango::Device_6Impl>
{
  public:
    Device_6ImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
        Device_XImplWrap(_self, cl, st){};

    Device_6ImplWrap(PyObject *_self,
                     CppDeviceClass *cl,
                     const char *name,
                     const char *_desc = "A Tango device",
                     Tango::DevState sta = Tango::UNKNOWN,
                     const char *status = Tango::StatusNotSet) :
        Device_XImplWrap(_self, cl, name, _desc, sta, status){};

    /**
     * I do not know why, but boost does link methods from template,
     * so we must have them implemented in wrapper (or I do something wrong)
     * so I just add simplest realization, which just call the parent method
     */

    void default_server_init_hook()
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_server_init_hook();
    }

    void default_delete_device()
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_delete_device();
    }

    void default_always_executed_hook()
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_always_executed_hook();
    }

    void default_read_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_read_attr_hardware(attr_list);
    }

    void default_write_attr_hardware(std::vector<long> &attr_list)
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_write_attr_hardware(attr_list);
    }

    Tango::DevState default_dev_state()
    {
        return Device_XImplWrap<Tango::Device_6Impl>::default_dev_state();
    }

    Tango::ConstDevString default_dev_status()
    {
        return Device_XImplWrap<Tango::Device_6Impl>::default_dev_status();
    }

    void default_signal_handler(long signo)
    {
        Device_XImplWrap<Tango::Device_6Impl>::default_signal_handler(signo);
    }
};

#endif // _DEVICE_IMPL_H
