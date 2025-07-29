/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"
#include "exception.h"
#include "to_py.h"
#include "server/device_impl.h"
#include "server/attr.h"
#include "server/attribute.h"
#include "server/command.h"
#include "server/pipe.h"

#include <boost/utility/enable_if.hpp>

extern const char *param_must_be_seq;

// cppTango since 9.4 version provides a way to stream in code location
// information wrapped in a LoggerStream::SourceLocation struct. Below
// template is used as a fallback if this struct is not defined. If it
// is and has non-zero size, the specialization defined later is used.
template <typename Stream, typename = void>
struct LogToStreamImpl
{
    static void log(Stream &stream, const std::string & /*file*/, int /*line*/, const std::string &msg)
    {
        stream << log4tango::_begin_log << msg;
    }
};

template <typename Stream>
struct LogToStreamImpl<Stream, typename boost::enable_if_c<(sizeof(typename Stream::SourceLocation) > 0)>::type>
{
    static void log(Stream &stream, const std::string &file, int line, const std::string &msg)
    {
        typename Stream::SourceLocation location = {file.c_str(), line};
        stream << log4tango::_begin_log << location << msg;
    }
};

static void log_to_stream(log4tango::LoggerStream &stream, const std::string &file, int line, const std::string &msg)
{
    LogToStreamImpl<log4tango::LoggerStream>::log(stream, file, line, msg);
}

#define SAFE_PUSH(dev, attr, attr_name)                                                   \
    std::string __att_name = bopy::extract<std::string>(attr_name);                       \
    AutoPythonAllowThreads python_guard_ptr;                                              \
    Tango::AutoTangoMonitor tango_guard(&dev);                                            \
    Tango::Attribute &attr = dev.get_device_attr()->get_attr_by_name(__att_name.c_str()); \
    (void) attr;                                                                          \
    python_guard_ptr.giveup();

#define AUX_SAFE_PUSH_EVENT(dev, attr_name, filt_names, filt_vals)    \
    StdStringVector filt_names_;                                      \
    StdDoubleVector filt_vals_;                                       \
    from_sequence<StdStringVector>::convert(filt_names, filt_names_); \
    from_sequence<StdDoubleVector>::convert(filt_vals, filt_vals_);   \
    SAFE_PUSH(dev, attr, attr_name)

#define SAFE_PUSH_EVENT_VARGS(dev, attr_name, filt_names, filt_vals, data, ...) \
    {                                                                           \
        AUX_SAFE_PUSH_EVENT(dev, attr_name, filt_names, filt_vals)              \
        PyAttribute::set_value(attr, data, __VA_ARGS__);                        \
        attr.fire_event(filt_names_, filt_vals_);                               \
    }

#define SAFE_PUSH_EVENT_DATE_QUALITY(dev, attr_name, filt_names, filt_vals, data, date, quality) \
    {                                                                                            \
        AUX_SAFE_PUSH_EVENT(dev, attr_name, filt_names, filt_vals)                               \
        PyAttribute::set_value_date_quality(attr, data, date, quality);                          \
        attr.fire_event(filt_names_, filt_vals_);                                                \
    }

#define SAFE_PUSH_EVENT_DATE_QUALITY_VARGS(dev, attr_name, filt_names, filt_vals, data, date, quality, ...) \
    {                                                                                                       \
        AUX_SAFE_PUSH_EVENT(dev, attr_name, filt_names, filt_vals)                                          \
        PyAttribute::set_value_date_quality(attr, data, date, quality, __VA_ARGS__);                        \
        attr.fire_event(filt_names_, filt_vals_);                                                           \
    }

namespace PyDeviceImpl
{
inline PyObject *get_polled_cmd(Tango::DeviceImpl &self)
{
    return to_list<std::vector<std::string>>::convert(self.get_polled_cmd());
}

inline PyObject *get_polled_attr(Tango::DeviceImpl &self)
{
    return to_list<std::vector<std::string>>::convert(self.get_polled_attr());
}

inline PyObject *get_non_auto_polled_cmd(Tango::DeviceImpl &self)
{
    return to_list<std::vector<std::string>>::convert(self.get_non_auto_polled_cmd());
}

inline PyObject *get_non_auto_polled_attr(Tango::DeviceImpl &self)
{
    return to_list<std::vector<std::string>>::convert(self.get_non_auto_polled_attr());
}

inline bopy::dict get_version_info_dict(Tango::DeviceImpl &self)
{
    bopy::dict result;
    Tango::DevInfoVersionList list = self.get_version_info();
    for(size_t i = 0; i < list.length(); ++i)
    {
        if(list[i].key != NULL && list[i].value != NULL)
        {
            // Insert into the dictionary
            result[list[i].key] = list[i].value;
        }
    }
    return result;
}

#if defined(TANGO_USE_TELEMETRY)
inline bool is_telemetry_enabled(Tango::DeviceImpl &self)
{
    if(self.telemetry())
    {
        return self.telemetry()->is_enabled();
    }
    else
    {
        return false;
    }
}

inline bool is_kernel_tracing_enabled(Tango::DeviceImpl &self)
{
    if(self.telemetry())
    {
        return self.telemetry()->are_kernel_traces_enabled();
    }
    else
    {
        return false;
    }
}
#endif

/* **********************************
 * firing change event
 * **********************************/

/* **********************************
 * change event USING set_vale
 * **********************************/

inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name)
{
    bopy::str name_lower = name.lower();
    if("state" != name_lower && "status" != name_lower)
    {
        Tango::Except::throw_exception("PyDs_InvalidCall",
                                       "push_change_event without data parameter is only allowed for "
                                       "state and status attributes.",
                                       "DeviceImpl::push_change_event");
    }
    SAFE_PUSH(self, attr, name)
    attr.set_value_flag(false);
    attr.fire_change_event();
}

inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data)
{
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        SAFE_PUSH(self, attr, name);
        attr.fire_change_event(const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data);
    attr.fire_change_event(nullptr);
}

// Special variation for encoded data type
inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::str &data)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_change_event();
}

// Special variation for encoded data type
inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::object &data)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_change_event();
}

inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x);
    attr.fire_change_event();
}

inline void push_change_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x, y);
    attr.fire_change_event();
}

/* **********************************
 * change event USING set_value_date_quality
 * **********************************/

inline void push_change_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality);
    attr.fire_change_event();
}

// Special variation for encoded data type
inline void push_change_event(Tango::DeviceImpl &self,
                              bopy::str &name,
                              bopy::str &str_data,
                              bopy::str &data,
                              double t,
                              Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_change_event();
}

// Special variation for encoded data type
inline void push_change_event(Tango::DeviceImpl &self,
                              bopy::str &name,
                              bopy::str &str_data,
                              bopy::object &data,
                              double t,
                              Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_change_event();
}

inline void push_change_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x);
    attr.fire_change_event();
}

inline void push_change_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x, y);
    attr.fire_change_event();
}

/* **********************************
 * firing alarm event
 * **********************************/

/* **********************************
 * alarm event USING set_vale
 * **********************************/

inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name)
{
    bopy::str name_lower = name.lower();
    if("state" != name_lower)
    {
        Tango::Except::throw_exception("PyDs_InvalidCall",
                                       "push_alarm_event without data parameter is only allowed for "
                                       "state attribute.",
                                       "DeviceImpl::push_alarm_event");
    }
    SAFE_PUSH(self, attr, name)
    attr.fire_alarm_event(nullptr);
}

inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data)
{
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        SAFE_PUSH(self, attr, name);
        attr.fire_alarm_event(const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data);
    attr.fire_alarm_event(nullptr);
}

// Special variation for encoded data type
inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::str &data)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_alarm_event(nullptr);
}

// Special variation for encoded data type
inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::object &data)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_alarm_event(nullptr);
}

inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x);
    attr.fire_alarm_event(nullptr);
}

inline void push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x, y);
    attr.fire_alarm_event(nullptr);
}

/* **********************************
 * alarm event USING set_value_date_quality
 * **********************************/

inline void
    push_alarm_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality);
    attr.fire_alarm_event(nullptr);
}

// Special variation for encoded data type
inline void push_alarm_event(Tango::DeviceImpl &self,
                             bopy::str &name,
                             bopy::str &str_data,
                             bopy::str &data,
                             double t,
                             Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_alarm_event(nullptr);
}

// Special variation for encoded data type
inline void push_alarm_event(Tango::DeviceImpl &self,
                             bopy::str &name,
                             bopy::str &str_data,
                             bopy::object &data,
                             double t,
                             Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_alarm_event(nullptr);
}

inline void push_alarm_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x);
    attr.fire_alarm_event(nullptr);
}

inline void push_alarm_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x, y);
    attr.fire_alarm_event(nullptr);
}

/* **********************************
 * firing archive event
 * **********************************/

/* **********************************
 * archive event USING set_value
 * **********************************/
inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name)
{
    bopy::str name_lower = name.lower();
    if("state" != name_lower && "status" != name_lower)
    {
        Tango::Except::throw_exception("PyDs_InvalidCall",
                                       "push_archive_event without data parameter is only allowed for "
                                       "state and status attributes.",
                                       "DeviceImpl::push_archive_event");
    }
    SAFE_PUSH(self, attr, name)
    attr.set_value_flag(false);
    attr.fire_archive_event();
}

inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data)
{
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        SAFE_PUSH(self, attr, name);
        attr.fire_archive_event(const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data);
    attr.fire_archive_event();
}

// Special variation for encoded data type
inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::str &data)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_archive_event();
}

// Special variation for encoded data type
inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name, bopy::str &str_data, bopy::object &data)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_archive_event();
}

inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x);
    attr.fire_archive_event();
}

inline void push_archive_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value(attr, data, x, y);
    attr.fire_archive_event();
}

/* **********************************
 * archive event USING set_value_date_quality
 * **********************************/

inline void push_archive_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality);
    attr.fire_archive_event();
}

// Special variation for encoded data type
inline void push_archive_event(Tango::DeviceImpl &self,
                               bopy::str &name,
                               bopy::str &str_data,
                               bopy::str &data,
                               double t,
                               Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_archive_event();
}

// Special variation for encoded data type
inline void push_archive_event(Tango::DeviceImpl &self,
                               bopy::str &name,
                               bopy::str &str_data,
                               bopy::object &data,
                               double t,
                               Tango::AttrQuality quality)
{
    SAFE_PUSH(self, attr, name)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_archive_event();
}

inline void push_archive_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x);
    attr.fire_archive_event();
}

inline void push_archive_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &data, double t, Tango::AttrQuality quality, long x, long y)
{
    SAFE_PUSH(self, attr, name);
    PyAttribute::set_value_date_quality(attr, data, t, quality, x, y);
    attr.fire_archive_event();
}

/* **********************************
 * firing user event
 * **********************************/

/* **********************************
 * user event USING set_value
 * **********************************/
inline void push_event(Tango::DeviceImpl &self, bopy::str &name, bopy::object &filt_names, bopy::object &filt_vals)
{
    bopy::str name_lower = name.lower();
    if("state" != name_lower && "status" != name_lower)
    {
        Tango::Except::throw_exception("PyDs_InvalidCall",
                                       "push_event without data parameter is only allowed for "
                                       "state and status attributes.",
                                       "DeviceImpl::push_event");
    }
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    attr.set_value_flag(false);
    attr.fire_event(filt_names_, filt_vals_);
}

inline void push_event(
    Tango::DeviceImpl &self, bopy::str &name, bopy::object &filt_names, bopy::object &filt_vals, bopy::object &data)
{
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    bopy::extract<Tango::DevFailed> except_convert(data);
    if(except_convert.check())
    {
        attr.fire_event(filt_names_, filt_vals_, const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    PyAttribute::set_value(attr, data);
    attr.fire_event(filt_names_, filt_vals_);
}

// Special variation for encoded data type
inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::str &str_data,
                       bopy::str &data)
{
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_event(filt_names_, filt_vals_);
}

// Special variation for encoded data type
inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::str &str_data,
                       bopy::object &data)
{
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    PyAttribute::set_value(attr, str_data, data);
    attr.fire_event(filt_names_, filt_vals_);
}

inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::object &data,
                       long x)
{
    SAFE_PUSH_EVENT_VARGS(self, name, filt_names, filt_vals, data, x)
}

inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::object &data,
                       long x,
                       long y)
{
    SAFE_PUSH_EVENT_VARGS(self, name, filt_names, filt_vals, data, x, y)
}

/* ***************************************
 * user event USING set_value_date_quality
 * **************************************/

inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::object &data,
                       double t,
                       Tango::AttrQuality quality)
{
    SAFE_PUSH_EVENT_DATE_QUALITY(self, name, filt_names, filt_vals, data, t, quality)
}

// Special variation for encoded data type
inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::str &str_data,
                       bopy::str &data,
                       double t,
                       Tango::AttrQuality quality)
{
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_event(filt_names_, filt_vals_);
}

// Special variation for encoded data type
inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::str &str_data,
                       bopy::object &data,
                       double t,
                       Tango::AttrQuality quality)
{
    AUX_SAFE_PUSH_EVENT(self, name, filt_names, filt_vals)
    PyAttribute::set_value_date_quality(attr, str_data, data, t, quality);
    attr.fire_event(filt_names_, filt_vals_);
}

inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::object &data,
                       double t,
                       Tango::AttrQuality quality,
                       long x)
{
    SAFE_PUSH_EVENT_DATE_QUALITY_VARGS(self, name, filt_names, filt_vals, data, t, quality, x)
}

inline void push_event(Tango::DeviceImpl &self,
                       bopy::str &name,
                       bopy::object &filt_names,
                       bopy::object &filt_vals,
                       bopy::object &data,
                       double t,
                       Tango::AttrQuality quality,
                       long x,
                       long y)
{
    SAFE_PUSH_EVENT_DATE_QUALITY_VARGS(self, name, filt_names, filt_vals, data, t, quality, x, y)
}

/* **********************************
 * data ready event
 * **********************************/
inline void push_data_ready_event(Tango::DeviceImpl &self, const bopy::str &name, long ctr)
{
    SAFE_PUSH(self, attr, name)
    self.push_data_ready_event(__att_name, ctr); //__att_name from SAFE_PUSH
}

/* **********************************
 * pipe event
 * **********************************/
inline void push_pipe_event(Tango::DeviceImpl &self, bopy::str &pipe_name, bopy::object &pipe_data)
{
    std::string __pipe_name = from_str_to_char(pipe_name.ptr());
    bopy::extract<Tango::DevFailed> except_convert(pipe_data);
    if(except_convert.check())
    {
        self.push_pipe_event(__pipe_name, const_cast<Tango::DevFailed *>(&except_convert()));
        return;
    }
    Tango::DevicePipeBlob dpb;
    bool reuse = false;
    PyDevicePipe::set_value(dpb, pipe_data);
    self.push_pipe_event(__pipe_name, &dpb, reuse);
}

void check_attribute_method_defined(PyObject *self, const std::string &attr_name, const std::string &method_name)
{
    bool exists, is_method;

    is_method_defined(self, method_name, exists, is_method);

    if(!exists)
    {
        TangoSys_OMemStream o;
        o << "Wrong definition of attribute " << attr_name << "\nThe attribute method " << method_name
          << " does not exist in your class!" << std::ends;

        Tango::Except::throw_exception(
            (const char *) "PyDs_WrongCommandDefinition", o.str(), (const char *) "check_attribute_method_defined");
    }

    if(!is_method)
    {
        TangoSys_OMemStream o;
        o << "Wrong definition of attribute " << attr_name << "\nThe object " << method_name
          << " exists in your class but is not a Python method" << std::ends;

        Tango::Except::throw_exception(
            (const char *) "PyDs_WrongCommandDefinition", o.str(), (const char *) "check_attribute_method_defined");
    }
}

void add_attribute(Tango::DeviceImpl &self,
                   const Tango::Attr &c_new_attr,
                   bopy::object read_meth_name,
                   bopy::object write_meth_name,
                   bopy::object is_allowed_meth_name)
{
    Tango::Attr &new_attr = const_cast<Tango::Attr &>(c_new_attr);

    std::string attr_name = new_attr.get_name();
    std::string read_name_met;
    std::string write_name_met;
    std::string is_allowed_method;

    if(read_meth_name.ptr() == Py_None)
    {
        read_name_met = "read_" + attr_name;
    }
    else
    {
        read_name_met = bopy::extract<std::string>(read_meth_name);
    }

    if(write_meth_name.ptr() == Py_None)
    {
        write_name_met = "write_" + attr_name;
    }
    else
    {
        write_name_met = bopy::extract<std::string>(write_meth_name);
    }

    if(is_allowed_meth_name.ptr() == Py_None)
    {
        is_allowed_method = "is_" + attr_name + "_allowed";
    }
    else
    {
        is_allowed_method = bopy::extract<std::string>(is_allowed_meth_name);
    }

    Tango::AttrWriteType attr_write = new_attr.get_writable();

    //
    // Create the attribute object according to attribute format
    //

    PyScaAttr *sca_attr_ptr = NULL;
    PySpecAttr *spec_attr_ptr = NULL;
    PyImaAttr *ima_attr_ptr = NULL;
    PyAttr *py_attr_ptr = NULL;
    Tango::Attr *attr_ptr = NULL;

    long x, y;
    std::vector<Tango::AttrProperty> &def_prop = new_attr.get_user_default_properties();
    Tango::AttrDataFormat attr_format = new_attr.get_format();
    long attr_type = new_attr.get_type();

    switch(attr_format)
    {
    case Tango::SCALAR:
        sca_attr_ptr = new PyScaAttr(attr_name, attr_type, attr_write, def_prop);
        py_attr_ptr = sca_attr_ptr;
        attr_ptr = sca_attr_ptr;
        break;

    case Tango::SPECTRUM:
        x = (static_cast<Tango::SpectrumAttr &>(new_attr)).get_max_x();
        spec_attr_ptr = new PySpecAttr(attr_name, attr_type, attr_write, x, def_prop);
        py_attr_ptr = spec_attr_ptr;
        attr_ptr = spec_attr_ptr;
        break;

    case Tango::IMAGE:
        x = (static_cast<Tango::ImageAttr &>(new_attr)).get_max_x();
        y = (static_cast<Tango::ImageAttr &>(new_attr)).get_max_y();
        ima_attr_ptr = new PyImaAttr(attr_name, attr_type, attr_write, x, y, def_prop);
        py_attr_ptr = ima_attr_ptr;
        attr_ptr = ima_attr_ptr;
        break;

    default:
        TangoSys_OMemStream o;
        o << "Attribute " << attr_name << " has an unexpected data format\n"
          << "Please report this bug to the PyTango development team" << std::ends;
        Tango::Except::throw_exception(
            (const char *) "PyDs_UnexpectedAttributeFormat", o.str(), (const char *) "cpp_add_attribute");
        break;
    }

    py_attr_ptr->set_read_name(read_name_met);
    py_attr_ptr->set_write_name(write_name_met);
    py_attr_ptr->set_allowed_name(is_allowed_method);

    if(new_attr.get_memorized())
    {
        attr_ptr->set_memorized();
    }
    attr_ptr->set_memorized_init(new_attr.get_memorized_init());

    attr_ptr->set_disp_level(new_attr.get_disp_level());
    attr_ptr->set_polling_period(new_attr.get_polling_period());
    attr_ptr->set_change_event(new_attr.is_change_event(), new_attr.is_check_change_criteria());
    attr_ptr->set_archive_event(new_attr.is_archive_event(), new_attr.is_check_archive_criteria());
    attr_ptr->set_data_ready_event(new_attr.is_data_ready_event());

    //
    // Install attribute in Tango. GIL is released during this operation
    //

    // so we have to release GIL
    AutoPythonAllowThreads guard;

    self.add_attribute(attr_ptr);
}

void remove_attribute(Tango::DeviceImpl &self, const char *att_name, bool free_it = false, bool clean_db = true)
{
    // We release GIL here
    AutoPythonAllowThreads guard;
    std::string str(att_name);
    self.remove_attribute(str, free_it, clean_db);
}

void add_command(Tango::DeviceImpl &self,
                 bopy::object cmd_name,
                 bopy::object cmd_data,
                 bopy::object is_allowed_name,
                 bopy::object disp_level,
                 bool device_level = false)
{
    std::string name = bopy::extract<std::string>(cmd_name);

    std::string in_desc = bopy::extract<std::string>(cmd_data[0][1]);
    std::string out_desc = bopy::extract<std::string>(cmd_data[1][1]);

    std::string is_allowed = bopy::extract<std::string>(is_allowed_name);

    Tango::CmdArgType argtype_in = bopy::extract<Tango::CmdArgType>(cmd_data[0][0]);
    Tango::CmdArgType argtype_out = bopy::extract<Tango::CmdArgType>(cmd_data[1][0]);
    Tango::DispLevel display_level = bopy::extract<Tango::DispLevel>(disp_level);

    PyCmd *cmd_ptr = new PyCmd(name, argtype_in, argtype_out, in_desc, out_desc, display_level);

    if(!is_allowed.empty())
    {
        cmd_ptr->set_allowed(is_allowed);
    }

    //
    // Install the command in Tango.
    //

    self.add_command(cmd_ptr, device_level);
}

void remove_command(Tango::DeviceImpl &self, bopy::object cmd_name, bool free_it = false, bool clean_db = true)
{
    std::string name = bopy::extract<std::string>(cmd_name);
    self.remove_command(name, free_it, clean_db);
}

inline void debug(Tango::DeviceImpl &self, const std::string &file, int line, const std::string &msg)
{
    if(self.get_logger()->is_debug_enabled())
    {
        log4tango::LoggerStream stream = self.get_logger()->debug_stream();
        log_to_stream(stream, file, line, msg);
    }
}

inline void info(Tango::DeviceImpl &self, const std::string &file, int line, const std::string &msg)
{
    if(self.get_logger()->is_info_enabled())
    {
        log4tango::LoggerStream stream = self.get_logger()->info_stream();
        log_to_stream(stream, file, line, msg);
    }
}

inline void warn(Tango::DeviceImpl &self, const std::string &file, int line, const std::string &msg)
{
    if(self.get_logger()->is_warn_enabled())
    {
        log4tango::LoggerStream stream = self.get_logger()->warn_stream();
        log_to_stream(stream, file, line, msg);
    }
}

inline void error(Tango::DeviceImpl &self, const std::string &file, int line, const std::string &msg)
{
    if(self.get_logger()->is_error_enabled())
    {
        log4tango::LoggerStream stream = self.get_logger()->error_stream();
        log_to_stream(stream, file, line, msg);
    }
}

inline void fatal(Tango::DeviceImpl &self, const std::string &file, int line, const std::string &msg)
{
    if(self.get_logger()->is_fatal_enabled())
    {
        log4tango::LoggerStream stream = self.get_logger()->fatal_stream();
        log_to_stream(stream, file, line, msg);
    }
}

PyObject *get_attribute_config(Tango::DeviceImpl &self, bopy::object &py_attr_name_seq)
{
    Tango::DevVarStringArray par;
    convert2array(py_attr_name_seq, par);

    Tango::AttributeConfigList *attr_conf_list_ptr = self.get_attribute_config(par);

    bopy::list ret = to_py(*attr_conf_list_ptr);
    delete attr_conf_list_ptr;

    return bopy::incref(ret.ptr());
}

void set_attribute_config(Tango::DeviceImpl &self, bopy::object &py_attr_conf_list)
{
    Tango::AttributeConfigList attr_conf_list;
    from_py_object(py_attr_conf_list, attr_conf_list);
    self.set_attribute_config(attr_conf_list);
}

bool is_attribute_polled(Tango::DeviceImpl &self, const std::string &att_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    return self_w->_is_attribute_polled(att_name);
}

bool is_command_polled(Tango::DeviceImpl &self, const std::string &cmd_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    return self_w->_is_command_polled(cmd_name);
}

int get_attribute_poll_period(Tango::DeviceImpl &self, const std::string &att_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    return self_w->_get_attribute_poll_period(att_name);
}

int get_command_poll_period(Tango::DeviceImpl &self, const std::string &cmd_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    return self_w->_get_command_poll_period(cmd_name);
}

void poll_attribute(Tango::DeviceImpl &self, const std::string &att_name, int period)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    self_w->_poll_attribute(att_name, period);
}

void poll_command(Tango::DeviceImpl &self, const std::string &cmd_name, int period)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    self_w->_poll_command(cmd_name, period);
}

void stop_poll_attribute(Tango::DeviceImpl &self, const std::string &att_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    self_w->_stop_poll_attribute(att_name);
}

void stop_poll_command(Tango::DeviceImpl &self, const std::string &cmd_name)
{
    DeviceImplWrap *self_w = (DeviceImplWrap *) (&self);
    self_w->_stop_poll_command(cmd_name);
}
} // namespace PyDeviceImpl

DeviceImplWrap::DeviceImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
    Tango::DeviceImpl(cl, st),
    m_self(_self)
{
    Py_INCREF(m_self);
}

DeviceImplWrap::DeviceImplWrap(PyObject *_self,
                               CppDeviceClass *cl,
                               const char *name,
                               const char *_desc /* = "A Tango device" */,
                               Tango::DevState sta /* = Tango::UNKNOWN */,
                               const char *status /* = StatusNotSet */) :
    Tango::DeviceImpl(cl, name, _desc, sta, status),
    m_self(_self)
{
    Py_INCREF(m_self);
}

void DeviceImplWrap::init_device()
{
    this->get_override("init_device")();
}

bool DeviceImplWrap::_is_attribute_polled(const std::string &att_name)
{
    return this->is_attribute_polled(att_name);
}

bool DeviceImplWrap::_is_command_polled(const std::string &cmd_name)
{
    return this->is_command_polled(cmd_name);
}

int DeviceImplWrap::_get_attribute_poll_period(const std::string &att_name)
{
    return this->get_attribute_poll_period(att_name);
}

int DeviceImplWrap::_get_command_poll_period(const std::string &cmd_name)
{
    return this->get_command_poll_period(cmd_name);
}

void DeviceImplWrap::_poll_attribute(const std::string &att_name, int period)
{
    this->poll_attribute(att_name, period);
}

void DeviceImplWrap::_poll_command(const std::string &cmd_name, int period)
{
    this->poll_command(cmd_name, period);
}

void DeviceImplWrap::_stop_poll_attribute(const std::string &att_name)
{
    this->stop_poll_attribute(att_name);
}

void DeviceImplWrap::_stop_poll_command(const std::string &cmd_name)
{
    this->stop_poll_command(cmd_name);
}

Device_2ImplWrap::Device_2ImplWrap(PyObject *_self, CppDeviceClass *cl, std::string &st) :
    Tango::Device_2Impl(cl, st),
    m_self(_self)
{
    Py_INCREF(m_self);
}

Device_2ImplWrap::Device_2ImplWrap(PyObject *_self,
                                   CppDeviceClass *cl,
                                   const char *name,
                                   const char *_desc /* = "A Tango device" */,
                                   Tango::DevState sta /* = Tango::UNKNOWN */,
                                   const char *status /* = StatusNotSet */) :
    Tango::Device_2Impl(cl, name, _desc, sta, status),
    m_self(_self)
{
    Py_INCREF(m_self);
}

void Device_2ImplWrap::init_device()
{
    this->get_override("init_device")();
}

namespace PyDevice_2Impl
{
PyObject *get_attribute_config_2(Tango::Device_2Impl &self, bopy::object &attr_name_seq)
{
    Tango::DevVarStringArray par;
    convert2array(attr_name_seq, par);

    Tango::AttributeConfigList_2 *attr_conf_list_ptr = self.get_attribute_config_2(par);

    bopy::list ret = to_py(*attr_conf_list_ptr);
    delete attr_conf_list_ptr;

    return bopy::incref(ret.ptr());
}

} // namespace PyDevice_2Impl

namespace PyDevice_3Impl
{
PyObject *get_attribute_config_3(Tango::Device_3Impl &self, bopy::object &attr_name_seq)
{
    Tango::DevVarStringArray par;
    convert2array(attr_name_seq, par);

    Tango::AttributeConfigList_3 *attr_conf_list_ptr = self.get_attribute_config_3(par);

    bopy::list ret = to_py(*attr_conf_list_ptr);
    delete attr_conf_list_ptr;

    return bopy::incref(ret.ptr());
}

void set_attribute_config_3(Tango::Device_3Impl &self, bopy::object &py_attr_conf_list)
{
    Tango::AttributeConfigList_3 attr_conf_list;
    from_py_object(py_attr_conf_list, attr_conf_list);
    self.set_attribute_config_3(attr_conf_list);
}

} // namespace PyDevice_3Impl

void no_op_void_handler_method(PyObject *self) { }

bool always_false(PyObject *self)
{
    return false;
}

#if((defined sun) || (defined WIN32))
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(register_signal_overload, Tango::DeviceImpl::register_signal, 1, 1)
#else
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(register_signal_overload, Tango::DeviceImpl::register_signal, 1, 2)
#endif

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(append_status_overload, Tango::DeviceImpl::append_status, 1, 2)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_change_event_overload, Tango::DeviceImpl::set_change_event, 2, 3)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_alarm_event_overload, Tango::DeviceImpl::set_alarm_event, 2, 3)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(set_archive_event_overload, Tango::DeviceImpl::set_archive_event, 2, 3)

void export_device_impl()
{
    void (Tango::DeviceImpl::*stop_polling1)() = &Tango::DeviceImpl::stop_polling;
    void (Tango::DeviceImpl::*stop_polling2)(bool) = &Tango::DeviceImpl::stop_polling;

    bopy::class_<Tango::DeviceImpl, std::shared_ptr<DeviceImplWrap>, boost::noncopyable>(
        "DeviceImpl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())

        .def("init_device", bopy::pure_virtual(&Tango::DeviceImpl::init_device))
        .def("set_state", &Tango::DeviceImpl::set_state)
        .def("get_state", &Tango::DeviceImpl::get_state, bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("get_prev_state",
             &Tango::DeviceImpl::get_prev_state,
             bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("get_name", &Tango::DeviceImpl::get_name, bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("get_device_attr",
             &Tango::DeviceImpl::get_device_attr,
             bopy::return_value_policy<bopy::reference_existing_object>())
        .def("register_signal", &Tango::DeviceImpl::register_signal, register_signal_overload())
        .def("unregister_signal", &Tango::DeviceImpl::unregister_signal)
        .def("get_status", &Tango::DeviceImpl::get_status, bopy::return_value_policy<bopy::copy_non_const_reference>())
        .def("set_status", &Tango::DeviceImpl::set_status)
        .def("append_status", &Tango::DeviceImpl::append_status, append_status_overload())
        .def("dev_state", &Tango::DeviceImpl::dev_state)
        .def("dev_status", &Tango::DeviceImpl::dev_status)
        .def("set_attribute_config", &PyDeviceImpl::set_attribute_config)
        .def("get_attribute_config", &PyDeviceImpl::get_attribute_config)
        .def("set_change_event", &Tango::DeviceImpl::set_change_event, set_change_event_overload())
        .def("set_alarm_event", &Tango::DeviceImpl::set_alarm_event, set_alarm_event_overload())
        .def("set_archive_event", &Tango::DeviceImpl::set_archive_event, set_archive_event_overload())
        .def("set_data_ready_event", &Tango::DeviceImpl::set_data_ready_event)
        .def("_add_attribute", &PyDeviceImpl::add_attribute)
        .def("_remove_attribute", &PyDeviceImpl::remove_attribute)
        .def("_add_command", &PyDeviceImpl::add_command)
        .def("_remove_command", &PyDeviceImpl::remove_command)
        //@TODO .def("get_device_class")
        //@TODO .def("get_db_device")
        .def("is_attribute_polled", &PyDeviceImpl::is_attribute_polled)
        .def("is_command_polled", &PyDeviceImpl::is_command_polled)
        .def("get_attribute_poll_period", &PyDeviceImpl::get_attribute_poll_period)
        .def("get_command_poll_period", &PyDeviceImpl::get_command_poll_period)
        .def("poll_attribute", &PyDeviceImpl::poll_attribute)
        .def("poll_command", &PyDeviceImpl::poll_command)
        .def("stop_poll_attribute", &PyDeviceImpl::stop_poll_attribute)
        .def("stop_poll_command", &PyDeviceImpl::stop_poll_command)

        .def("get_exported_flag", &Tango::DeviceImpl::get_exported_flag)
        .def("get_poll_ring_depth", &Tango::DeviceImpl::get_poll_ring_depth)
        .def("get_poll_old_factor", &Tango::DeviceImpl::get_poll_old_factor)
        .def("is_polled", (bool(Tango::DeviceImpl::*)()) & Tango::DeviceImpl::is_polled)
        .def("get_polled_cmd", &PyDeviceImpl::get_polled_cmd)
        .def("get_polled_attr", &PyDeviceImpl::get_polled_attr)
        .def("get_non_auto_polled_cmd", &PyDeviceImpl::get_non_auto_polled_cmd)
        .def("get_non_auto_polled_attr", &PyDeviceImpl::get_non_auto_polled_attr)
        //@TODO .def("get_poll_obj_list", &PyDeviceImpl::get_poll_obj_list)
        .def("stop_polling", stop_polling1)
        .def("stop_polling", stop_polling2)
        .def("check_command_exists", &Tango::DeviceImpl::check_command_exists)
        //@TODO .def("get_command", &PyDeviceImpl::get_command)
        .def("get_dev_idl_version", &Tango::DeviceImpl::get_dev_idl_version)
        .def("get_cmd_poll_ring_depth",
             (long(Tango::DeviceImpl::*)(const std::string &)) & Tango::DeviceImpl::get_cmd_poll_ring_depth)
        .def("get_attr_poll_ring_depth",
             (long(Tango::DeviceImpl::*)(const std::string &)) & Tango::DeviceImpl::get_attr_poll_ring_depth)
        .def("is_device_locked", &Tango::DeviceImpl::is_device_locked)
        .def("add_version_info", &Tango::DeviceImpl::add_version_info)
        .def("get_version_info", &PyDeviceImpl::get_version_info_dict)

        .def("init_logger", &Tango::DeviceImpl::init_logger)
        .def("start_logging", &Tango::DeviceImpl::start_logging)
        .def("stop_logging", &Tango::DeviceImpl::stop_logging)

#if defined(TANGO_USE_TELEMETRY)
        .def("is_telemetry_enabled", &PyDeviceImpl::is_telemetry_enabled)
        .def("_enable_telemetry", &Tango::DeviceImpl::enable_telemetry)
        .def("_disable_telemetry", &Tango::DeviceImpl::disable_telemetry)
        .def("_enable_kernel_traces", &Tango::DeviceImpl::enable_kernel_traces)
        .def("_disable_kernel_traces", &Tango::DeviceImpl::disable_kernel_traces)
        .def("is_kernel_tracing_enabled", &PyDeviceImpl::is_kernel_tracing_enabled)
#else
        // If support for telemetry is not compiled in, we use no-op handlers, so the Python
        // code can still run without errors, but does nothing.
        .def("is_telemetry_enabled", &always_false)
        .def("_enable_telemetry", &no_op_void_handler_method)
        .def("_disable_telemetry", &no_op_void_handler_method)
        .def("is_kernel_tracing_enabled", &always_false)
        .def("_enable_kernel_traces", &no_op_void_handler_method)
        .def("_disable_kernel_traces", &no_op_void_handler_method)
#endif

        //.def("set_exported_flag", &Tango::DeviceImpl::set_exported_flag)
        //.def("set_poll_ring_depth", &Tango::DeviceImpl::set_poll_ring_depth)

        /* **********************************
         * firing change event
         * **********************************/

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &)) & PyDeviceImpl::push_change_event,
             (arg_("self"), arg_("attr_name")))

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &)) & PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &)) & PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &)) &
                 PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long)) & PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long, long)) & PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long)) &
                 PyDeviceImpl::push_change_event)

        .def("__push_change_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long, long)) &
                 PyDeviceImpl::push_change_event)

        /* **********************************
         * firing alarm event
         * **********************************/

        .def("__push_alarm_event", (void (*)(Tango::DeviceImpl &, bopy::str &)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long, long)) & PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long)) &
                 PyDeviceImpl::push_alarm_event)

        .def("__push_alarm_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long, long)) &
                 PyDeviceImpl::push_alarm_event)

        /* **********************************
         * firing archive event
         * **********************************/

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &)) & PyDeviceImpl::push_archive_event,
             (arg_("self"), arg_("attr_name")))

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &)) & PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &)) & PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long)) & PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, long, long)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::str &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::str &, bopy::object &, double, Tango::AttrQuality)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long)) &
                 PyDeviceImpl::push_archive_event)

        .def("__push_archive_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, double, Tango::AttrQuality, long, long)) &
                 PyDeviceImpl::push_archive_event)

        /* **********************************
         * firing user event
         * **********************************/

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &)) & PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &, bopy::object &)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &, bopy::str &, bopy::str &)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &, bopy::str &, bopy::object &)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &, bopy::object &, long)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &, bopy::object &, bopy::object &, long, long)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &,
                       bopy::str &,
                       bopy::object &,
                       bopy::object &,
                       bopy::object &,
                       double,
                       Tango::AttrQuality)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &,
                       bopy::str &,
                       bopy::object &,
                       bopy::object &,
                       bopy::str &,
                       bopy::str &,
                       double,
                       Tango::AttrQuality)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &,
                       bopy::str &,
                       bopy::object &,
                       bopy::object &,
                       bopy::str &,
                       bopy::object &,
                       double,
                       Tango::AttrQuality)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &,
                       bopy::str &,
                       bopy::object &,
                       bopy::object &,
                       bopy::object &,
                       double,
                       Tango::AttrQuality,
                       long)) &
                 PyDeviceImpl::push_event)

        .def("__push_event",
             (void (*)(Tango::DeviceImpl &,
                       bopy::str &,
                       bopy::object &,
                       bopy::object &,
                       bopy::object &,
                       double,
                       Tango::AttrQuality,
                       long,
                       long)) &
                 PyDeviceImpl::push_event)

        /* **********************************
         * firing data ready event
         * **********************************/
        .def("push_data_ready_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, long)) & PyDeviceImpl::push_data_ready_event,
             (arg_("self"), arg_("attr_name"), arg_("ctr")))

        /* **********************************
         * firing pipe event
         * **********************************/

        .def("push_pipe_event",
             (void (*)(Tango::DeviceImpl &, bopy::str &, bopy::object &)) & PyDeviceImpl::push_pipe_event,
             (arg_("self"), arg_("pipe_name"), arg_("pipe_data")))

        .def("push_att_conf_event", &Tango::DeviceImpl::push_att_conf_event)
        .def("get_logger", &Tango::DeviceImpl::get_logger, bopy::return_internal_reference<>())
        .def("__debug_stream", &PyDeviceImpl::debug)
        .def("__info_stream", &PyDeviceImpl::info)
        .def("__warn_stream", &PyDeviceImpl::warn)
        .def("__error_stream", &PyDeviceImpl::error)
        .def("__fatal_stream", &PyDeviceImpl::fatal)

        .def("get_min_poll_period", &Tango::DeviceImpl::get_min_poll_period)
        .def(
            "get_cmd_min_poll_period", &Tango::DeviceImpl::get_cmd_min_poll_period, bopy::return_internal_reference<>())
        .def("get_attr_min_poll_period",
             &Tango::DeviceImpl::get_attr_min_poll_period,
             bopy::return_internal_reference<>())
        .def("is_there_subscriber", &Tango::DeviceImpl::is_there_subscriber);
    bopy::implicitly_convertible<std::shared_ptr<DeviceImplWrap>, std::shared_ptr<Tango::DeviceImpl>>();

    bopy::class_<Tango::Device_2Impl, Device_2ImplWrap, bopy::bases<Tango::DeviceImpl>, boost::noncopyable>(
        "Device_2Impl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())
        .def("get_attribute_config_2", &PyDevice_2Impl::get_attribute_config_2)
        //@TODO .def("read_attribute_history_2", &PyDevice_2Impl::read_attribute_history_2)
        ;

    bopy::class_<Tango::Device_3Impl, Device_3ImplWrap, bopy::bases<Tango::Device_2Impl>, boost::noncopyable>(
        "Device_3Impl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())
        .def("init_device", bopy::pure_virtual(&Tango::Device_3Impl::init_device))
        .def("server_init_hook", &Tango::Device_3Impl::server_init_hook, &Device_3ImplWrap::default_server_init_hook)
        .def("delete_device", &Tango::Device_3Impl::delete_device, &Device_3ImplWrap::default_delete_device)
        .def("always_executed_hook",
             &Tango::Device_3Impl::always_executed_hook,
             &Device_3ImplWrap::default_always_executed_hook)
        .def("read_attr_hardware",
             &Tango::Device_3Impl::read_attr_hardware,
             &Device_3ImplWrap::default_read_attr_hardware)
        .def("write_attr_hardware",
             &Tango::Device_3Impl::write_attr_hardware,
             &Device_3ImplWrap::default_write_attr_hardware)
        .def("dev_state", &Tango::Device_3Impl::dev_state, &Device_3ImplWrap::default_dev_state)
        .def("dev_status", &Tango::Device_3Impl::dev_status, &Device_3ImplWrap::default_dev_status)
        .def("signal_handler", &Tango::Device_3Impl::signal_handler, &Device_3ImplWrap::default_signal_handler)
        .def("get_attribute_config_3", &PyDevice_3Impl::get_attribute_config_3)
        .def("set_attribute_config_3", &PyDevice_3Impl::set_attribute_config_3);

    bopy::class_<Tango::Device_4Impl,
                 std::shared_ptr<Device_4ImplWrap>,
                 bopy::bases<Tango::Device_3Impl>,
                 boost::noncopyable>(
        "Device_4Impl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())
        .def("init_device", bopy::pure_virtual(&Tango::Device_4Impl::init_device))
        .def("server_init_hook", &Tango::Device_4Impl::server_init_hook, &Device_4ImplWrap::default_server_init_hook)
        .def("delete_device", &Tango::Device_4Impl::delete_device, &Device_4ImplWrap::default_delete_device)
        .def("always_executed_hook",
             &Tango::Device_4Impl::always_executed_hook,
             &Device_4ImplWrap::default_always_executed_hook)
        .def("read_attr_hardware",
             &Tango::Device_4Impl::read_attr_hardware,
             &Device_4ImplWrap::default_read_attr_hardware)
        .def("write_attr_hardware",
             &Tango::Device_4Impl::write_attr_hardware,
             &Device_4ImplWrap::default_write_attr_hardware)
        .def("dev_state", &Tango::Device_4Impl::dev_state, &Device_4ImplWrap::default_dev_state)
        .def("dev_status", &Tango::Device_4Impl::dev_status, &Device_4ImplWrap::default_dev_status)
        .def("signal_handler", &Tango::Device_4Impl::signal_handler, &Device_4ImplWrap::default_signal_handler);
    bopy::implicitly_convertible<std::shared_ptr<Device_4ImplWrap>, std::shared_ptr<Tango::Device_4Impl>>();

    bopy::class_<Tango::Device_5Impl,
                 std::shared_ptr<Device_5ImplWrap>,
                 bopy::bases<Tango::Device_4Impl>,
                 boost::noncopyable>(
        "Device_5Impl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())
        .def("init_device", bopy::pure_virtual(&Tango::Device_5Impl::init_device))
        .def("server_init_hook", &Tango::Device_5Impl::server_init_hook, &Device_5ImplWrap::default_server_init_hook)
        .def("delete_device", &Tango::Device_5Impl::delete_device, &Device_5ImplWrap::default_delete_device)
        .def("always_executed_hook",
             &Tango::Device_5Impl::always_executed_hook,
             &Device_5ImplWrap::default_always_executed_hook)
        .def("read_attr_hardware",
             &Tango::Device_5Impl::read_attr_hardware,
             &Device_5ImplWrap::default_read_attr_hardware)
        .def("write_attr_hardware",
             &Tango::Device_5Impl::write_attr_hardware,
             &Device_5ImplWrap::default_write_attr_hardware)
        .def("dev_state", &Tango::Device_5Impl::dev_state, &Device_5ImplWrap::default_dev_state)
        .def("dev_status", &Tango::Device_5Impl::dev_status, &Device_5ImplWrap::default_dev_status)
        .def("signal_handler", &Tango::Device_5Impl::signal_handler, &Device_5ImplWrap::default_signal_handler);
    bopy::implicitly_convertible<std::shared_ptr<Device_5ImplWrap>, std::shared_ptr<Tango::Device_5Impl>>();

    bopy::class_<Tango::Device_6Impl,
                 std::shared_ptr<Device_6ImplWrap>,
                 bopy::bases<Tango::Device_5Impl>,
                 boost::noncopyable>(
        "Device_6Impl",
        bopy::init<CppDeviceClass *, const char *, bopy::optional<const char *, Tango::DevState, const char *>>())
        .def("init_device", bopy::pure_virtual(&Tango::Device_6Impl::init_device))
        .def("server_init_hook", &Tango::Device_6Impl::server_init_hook, &Device_6ImplWrap::default_server_init_hook)
        .def("delete_device", &Tango::Device_6Impl::delete_device, &Device_6ImplWrap::default_delete_device)
        .def("always_executed_hook",
             &Tango::Device_6Impl::always_executed_hook,
             &Device_6ImplWrap::default_always_executed_hook)
        .def("read_attr_hardware",
             &Tango::Device_6Impl::read_attr_hardware,
             &Device_6ImplWrap::default_read_attr_hardware)
        .def("write_attr_hardware",
             &Tango::Device_6Impl::write_attr_hardware,
             &Device_6ImplWrap::default_write_attr_hardware)
        .def("dev_state", &Tango::Device_6Impl::dev_state, &Device_6ImplWrap::default_dev_state)
        .def("dev_status", &Tango::Device_6Impl::dev_status, &Device_6ImplWrap::default_dev_status)
        .def("signal_handler", &Tango::Device_6Impl::signal_handler, &Device_6ImplWrap::default_signal_handler);
    bopy::implicitly_convertible<std::shared_ptr<Device_6ImplWrap>, std::shared_ptr<Tango::Device_6Impl>>();
}
