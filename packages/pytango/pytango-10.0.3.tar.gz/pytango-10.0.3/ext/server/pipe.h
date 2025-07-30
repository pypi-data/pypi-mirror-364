/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#pragma once

#include <boost/python.hpp>
#include <tango/tango.h>
#include "exception.h"
#include "pytgutils.h"
#include "server/device_impl.h"

namespace PyTango
{
namespace Pipe
{

class _Pipe
{
  public:
    _Pipe() { }

    virtual ~_Pipe() { }

    void read(Tango::DeviceImpl *, Tango::Pipe &);
    void write(Tango::DeviceImpl *dev, Tango::WPipe &);
    bool is_allowed(Tango::DeviceImpl *, Tango::PipeReqType);

    void set_allowed_name(const std::string &name)
    {
        py_allowed_name = name;
    }

    void set_read_name(const std::string &name)
    {
        read_name = name;
    }

    void set_write_name(const std::string &name)
    {
        write_name = name;
    }

    bool _is_method(Tango::DeviceImpl *, const std::string &);

  private:
    std::string py_allowed_name;
    std::string read_name;
    std::string write_name;
};

class PyPipe : public Tango::Pipe, public _Pipe
{
  public:
    PyPipe(const std::string &_name,
           const Tango::DispLevel level,
           const Tango::PipeWriteType write = Tango::PIPE_READ) :
        Tango::Pipe(_name, level, write)
    {
    }

    ~PyPipe() { }

    virtual void read(Tango::DeviceImpl *dev)
    {
        _Pipe::read(dev, *this);
    }

    virtual bool is_allowed(Tango::DeviceImpl *dev, Tango::PipeReqType rt)
    {
        return _Pipe::is_allowed(dev, rt);
    }
};

class PyWPipe : public Tango::WPipe, public _Pipe
{
  public:
    PyWPipe(const std::string &_name, const Tango::DispLevel level) :
        Tango::WPipe(_name, level)
    {
    }

    ~PyWPipe() { }

    virtual void read(Tango::DeviceImpl *dev)
    {
        _Pipe::read(dev, *this);
    }

    virtual void write(Tango::DeviceImpl *dev)
    {
        _Pipe::write(dev, *this);
    }

    virtual bool is_allowed(Tango::DeviceImpl *dev, Tango::PipeReqType rt)
    {
        return _Pipe::is_allowed(dev, rt);
    }
};

} // namespace Pipe
} // namespace PyTango

namespace PyDevicePipe
{
void set_value(Tango::DevicePipeBlob &, bopy::object &);

} // namespace PyDevicePipe
