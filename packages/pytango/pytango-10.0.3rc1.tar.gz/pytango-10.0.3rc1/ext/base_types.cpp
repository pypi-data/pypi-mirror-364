/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"
#include "defs.h"
#include "pytgutils.h"
#include "fast_from_py.h"
#include "base_types_numpy.hpp"

// from tango_const.h
void export_poll_device();

// from devapi.h
void export_locker_info();
// TODO void export_locking_thread();
void export_dev_command_info();
void export_attribute_dimension();
void export_command_info();
void export_device_info();
void export_device_attribute_config();
void export_attribute_info();
void export_attribute_alarm_info();
void export_change_event_info();
void export_periodic_event_info();
void export_archive_event_info();
void export_attribute_event_info();
void export_attribute_info_ex();
void export_device_data();
void export_device_attribute();
void export_device_data_history();
void export_device_attribute_history();
void export_device_pipe();
void export_pipe_info();

void export_dev_error();
void export_time_val();
void export_coverage_helper();

//
// Necessary equality operators for having vectors exported to python
//

namespace Tango
{

inline bool operator==(const Tango::DbDatum &dd1, const Tango::DbDatum &dd2)
{
    return dd1.name == dd2.name && dd1.value_string == dd2.value_string;
}

inline bool operator==(const Tango::DbDevInfo &di1, const Tango::DbDevInfo &di2)
{
    return di1.name == di2.name && di1._class == di2._class && di1.server == di2.server;
}

inline bool operator==(const Tango::DbDevImportInfo &dii1, const Tango::DbDevImportInfo &dii2)
{
    return dii1.name == dii2.name && dii1.exported == dii2.exported && dii1.ior == dii2.ior &&
           dii1.version == dii2.version;
}

inline bool operator==(const Tango::DbDevExportInfo &dei1, const Tango::DbDevExportInfo &dei2)
{
    return dei1.name == dei2.name && dei1.ior == dei2.ior && dei1.host == dei2.host && dei1.version == dei2.version &&
           dei1.pid == dei2.pid;
}

inline bool operator==(const Tango::DbHistory &dh1_, const Tango::DbHistory &dh2_)
{
    Tango::DbHistory &dh1 = const_cast<Tango::DbHistory &>(dh1_);
    Tango::DbHistory &dh2 = const_cast<Tango::DbHistory &>(dh2_);

    return dh1.get_name() == dh2.get_name() && dh1.get_attribute_name() == dh2.get_attribute_name() &&
           dh1.is_deleted() == dh2.is_deleted();
}

inline bool operator==(const Tango::GroupReply &dh1_, const Tango::GroupReply &dh2_)
{
    /// @todo ?
    return false;
}

inline bool operator==(const Tango::TimeVal &tv1, const Tango::TimeVal &tv2)
{
    return tv1.tv_sec == tv2.tv_sec && tv1.tv_usec == tv2.tv_usec && tv1.tv_nsec == tv2.tv_nsec;
}

inline bool operator==(const Tango::DeviceData &dd1_, const Tango::DeviceData &dd2_)
{
    Tango::DeviceData &dd1 = const_cast<Tango::DeviceData &>(dd1_);
    Tango::DeviceData &dd2 = const_cast<Tango::DeviceData &>(dd2_);

    return // dh1.any == dh2.any &&
        dd1.exceptions() == dd2.exceptions();
}

inline bool operator==(const Tango::DeviceDataHistory &ddh1_, const Tango::DeviceDataHistory &ddh2_)
{
    Tango::DeviceDataHistory &ddh1 = const_cast<Tango::DeviceDataHistory &>(ddh1_);
    Tango::DeviceDataHistory &ddh2 = const_cast<Tango::DeviceDataHistory &>(ddh2_);

    return operator==((Tango::DeviceData) ddh1, (Tango::DeviceData) ddh2) && ddh1.failed() == ddh2.failed() &&
           ddh1.date() == ddh2.date(); //&&
                                       // ddh1.errors() == ddh2.errors();
}

inline bool operator==(const Tango::PipeInfo &pi1, const Tango::PipeInfo &pi2)
{
    return pi1.name == pi2.name && pi1.description == pi2.description && pi1.label == pi2.label &&
           pi1.disp_level == pi2.disp_level && pi1.writable == pi2.writable && pi1.extensions == pi2.extensions;
}
} // namespace Tango

/**
 * Converter from python sequence to CORBA sequence
 */
template <typename CorbaSequence>
struct convert_PySequence_to_CORBA_Sequence
{
    convert_PySequence_to_CORBA_Sequence()
    {
        // Register converter from python sequence to CorbaSequence
        bopy::converter::registry::push_back(&convertible, &construct, bopy::type_id<CorbaSequence>());
    }

    // Check if given Python object is convertible to a sequence.
    // If so, return obj, otherwise return 0
    static void *convertible(PyObject *obj)
    {
        return (PySequence_Check(obj)) ? obj : NULL;
    }

    static void construct(PyObject *obj, bopy::converter::rvalue_from_python_stage1_data *data)
    {
        typedef bopy::converter::rvalue_from_python_storage<CorbaSequence> CorbaSequence_storage;

        void *const storage = reinterpret_cast<CorbaSequence_storage *>(data)->storage.bytes;

        CorbaSequence *ptr = new(storage) CorbaSequence();
        convert2array(bopy::object(bopy::handle<>(obj)), *ptr);
        data->convertible = storage;
    }
};

bool is_str(PyObject *obj)
{
    return PyBytes_Check(obj) || PyUnicode_Check(obj);
}

struct StdString_from_python_str_unicode
{
    StdString_from_python_str_unicode()
    {
        bopy::converter::registry::push_back(&convertible, &construct, bopy::type_id<std::string>());
    }

    // Determine if obj_ptr can be converted in a std::string
    static void *convertible(PyObject *obj)
    {
        if(!is_str(obj))
        {
            return 0;
        }
        return obj;
    }

    // Convert obj_ptr into a std::string
    static void construct(PyObject *obj, bopy::converter::rvalue_from_python_stage1_data *data)
    {
        bool decref = false;

        if(PyUnicode_Check(obj))
        {
            decref = true;
            obj = EncodeAsLatin1(obj);
        }

        const char *value = PyBytes_AsString(obj);
        Py_ssize_t size = PyBytes_Size(obj);

        // Grab pointer to memory into which to construct the new std::string
        void *storage = ((bopy::converter::rvalue_from_python_storage<std::string> *) data)->storage.bytes;

        // in-place construct the new std::string using the character data
        // extraced from the python object
        new(storage) std::string(value, size);

        // Stash the memory chunk pointer for later use by boost.python
        data->convertible = storage;

        if(decref)
        {
            Py_DECREF(obj);
        }
    }
};

PyObject *vector_string_get_item(const StdStringVector &vec, int index)
{
    size_t pos = index < 0 ? index + vec.size() : (size_t) index;
    if(pos >= vec.size())
    {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        bopy::throw_error_already_set();
        return NULL;
    }
    return from_char_to_python_str(vec[pos]);
}

void *convert_to_cstring(PyObject *obj)
{
    return PyBytes_Check(obj) ? PyBytes_AsString(obj) : 0;
}

int raise_asynch_exception(long thread_id, bopy::object exp_klass)
{
    return PyThreadState_SetAsyncExc(thread_id, exp_klass.ptr());
}

void export_base_types()
{
    // Add missing convert from python bytes to char *
    bopy::converter::registry::insert(
        convert_to_cstring, bopy::type_id<char>(), &bopy::converter::wrap_pytype<&PyBytes_Type>::get_pytype);

    bopy::enum_<PyTango::ExtractAs>("ExtractAs")
        .value("Numpy", PyTango::ExtractAsNumpy)
        .value("ByteArray", PyTango::ExtractAsByteArray)
        .value("Bytes", PyTango::ExtractAsBytes)
        .value("Tuple", PyTango::ExtractAsTuple)
        .value("List", PyTango::ExtractAsList)
        .value("String", PyTango::ExtractAsString)
        .value("Nothing", PyTango::ExtractAsNothing);

    bopy::enum_<PyTango::GreenMode>("GreenMode")
        .value("Synchronous", PyTango::GreenModeSynchronous)
        .value("Futures", PyTango::GreenModeFutures)
        .value("Gevent", PyTango::GreenModeGevent)
        .value("Asyncio", PyTango::GreenModeAsyncio);

    bopy::enum_<PyTango::ImageFormat>("_ImageFormat")
        .value("RawImage", PyTango::RawImage)
        .value("JpegImage", PyTango::JpegImage);

    // Export some std types

    // vector_indexing_suite<*, true | false>:
    //  - true:  Make a copy of the original value each time the vector
    //           is accessed. We have a struct like this:
    //              struct V { int value; }
    //            and the object is:
    //              std::vector<V> vec = { 69 };
    //            wrapped in python and we do:
    //              vec[0].value = 3
    //              vec[0].unexisting = 7
    //              print vec[0].value
    //              >> 69 ( 3 is stored in the obj created the first vec[0])
    //              print vec[0].unexisting
    //              >> exception (unexisting is stored in the other obj)
    //           If the C struct has a 'value' field, it will
    //  - false: Make a new proxy object of the original value each time
    //           the vector is accessed. With the same example:
    //              vec[0].value = 3
    //              vec[0].unexisting = 7
    //              print vec[0].value
    //              >> 3 (It's another proxy obj, but modifiyes the same
    //                   internal C object)
    //              print vec[0].unexisting
    //              >> exception (unexisting is stored in the other obj)

    bopy::class_<StdStringVector>("StdStringVector")
        .def(bopy::vector_indexing_suite<StdStringVector, true>())
        .def("__getitem__", &vector_string_get_item);

    bopy::class_<StdLongVector>("StdLongVector").def(bopy::vector_indexing_suite<StdLongVector, true>());

    bopy::class_<StdDoubleVector>("StdDoubleVector").def(bopy::vector_indexing_suite<StdDoubleVector, true>());

    bopy::class_<Tango::CommandInfoList>("CommandInfoList")
        .def(bopy::vector_indexing_suite<Tango::CommandInfoList, false>());

    bopy::class_<Tango::AttributeInfoList>("AttributeInfoList")
        .def(bopy::vector_indexing_suite<Tango::AttributeInfoList, false>());

    bopy::class_<Tango::AttributeInfoListEx>("AttributeInfoListEx")
        .def(bopy::vector_indexing_suite<Tango::AttributeInfoListEx, false>());

    bopy::class_<Tango::PipeInfoList>("PipeInfoList").def(bopy::vector_indexing_suite<Tango::PipeInfoList, false>());

    bopy::class_<std::vector<Tango::Attr *>>("AttrList")
        .def(bopy::vector_indexing_suite<std::vector<Tango::Attr *>, true>());

    bopy::class_<std::vector<Tango::Attribute *>>("AttributeList")
        .def(bopy::vector_indexing_suite<std::vector<Tango::Attribute *>, true>());

    bopy::class_<std::vector<Tango::Pipe *>>("PipeList")
        .def(bopy::vector_indexing_suite<std::vector<Tango::Pipe *>, true>());

    // class_<Tango::EventDataList>("EventDataList")
    //     .def(bopy::vector_indexing_suite<Tango::EventDataList>());

    bopy::class_<Tango::DbData>("DbData").def(bopy::vector_indexing_suite<Tango::DbData, true>());

    bopy::class_<Tango::DbDevInfos>("DbDevInfos").def(bopy::vector_indexing_suite<Tango::DbDevInfos, true>());

    bopy::class_<Tango::DbDevExportInfos>("DbDevExportInfos")
        .def(bopy::vector_indexing_suite<Tango::DbDevExportInfos, true>());

    bopy::class_<Tango::DbDevImportInfos>("DbDevImportInfos")
        .def(bopy::vector_indexing_suite<Tango::DbDevImportInfos, true>());

    bopy::class_<std::vector<Tango::DbHistory>>("DbHistoryList")
        .def(bopy::vector_indexing_suite<std::vector<Tango::DbHistory>, true>());

    bopy::class_<std::vector<Tango::DeviceData>>("DeviceDataList")
        .def(bopy::vector_indexing_suite<std::vector<Tango::DeviceData>, true>());

    bopy::class_<Tango::DeviceDataHistoryList>("DeviceDataHistoryList")
        .def(bopy::vector_indexing_suite<Tango::DeviceDataHistoryList, true>());

    typedef std::vector<Tango::GroupReply> StdGroupReplyVector_;
    bopy::class_<StdGroupReplyVector_>("StdGroupReplyVector")
        .def(bopy::vector_indexing_suite<StdGroupReplyVector_, true>());

    typedef std::vector<Tango::GroupCmdReply> StdGroupCmdReplyVector_;
    bopy::class_<StdGroupCmdReplyVector_>("StdGroupCmdReplyVector")
        .def(bopy::vector_indexing_suite<StdGroupCmdReplyVector_, true>());

    typedef std::vector<Tango::GroupAttrReply> StdGroupAttrReplyVector_;
    bopy::class_<StdGroupAttrReplyVector_>("StdGroupAttrReplyVector")
        .def(bopy::vector_indexing_suite<StdGroupAttrReplyVector_, true>());

    bopy::to_python_converter<CORBA::String_member, CORBA_String_member_to_str>();
    // bopy::to_python_converter<_CORBA_String_member, CORBA_String_member_to_str2>();
    bopy::to_python_converter<_CORBA_String_element, CORBA_String_element_to_str>();

    bopy::to_python_converter<Tango::DevErrorList, CORBA_sequence_to_tuple<Tango::DevErrorList>>();

    bopy::to_python_converter<Tango::DevVarCharArray, CORBA_sequence_to_list<Tango::DevVarCharArray>>();
    bopy::to_python_converter<Tango::DevVarShortArray, CORBA_sequence_to_list<Tango::DevVarShortArray>>();
    bopy::to_python_converter<Tango::DevVarLongArray, CORBA_sequence_to_list<Tango::DevVarLongArray>>();
    bopy::to_python_converter<Tango::DevVarFloatArray, CORBA_sequence_to_list<Tango::DevVarFloatArray>>();
    bopy::to_python_converter<Tango::DevVarDoubleArray, CORBA_sequence_to_list<Tango::DevVarDoubleArray>>();
    bopy::to_python_converter<Tango::DevVarUShortArray, CORBA_sequence_to_list<Tango::DevVarUShortArray>>();
    bopy::to_python_converter<Tango::DevVarULongArray, CORBA_sequence_to_list<Tango::DevVarULongArray>>();
    bopy::to_python_converter<Tango::DevVarStringArray, CORBA_sequence_to_list<Tango::DevVarStringArray>>();
    bopy::to_python_converter<Tango::DevVarLongStringArray, CORBA_sequence_to_list<Tango::DevVarLongStringArray>>();
    bopy::to_python_converter<Tango::DevVarDoubleStringArray, CORBA_sequence_to_list<Tango::DevVarDoubleStringArray>>();
    bopy::to_python_converter<Tango::DevVarLong64Array, CORBA_sequence_to_list<Tango::DevVarLong64Array>>();
    bopy::to_python_converter<Tango::DevVarULong64Array, CORBA_sequence_to_list<Tango::DevVarULong64Array>>();

    bopy::to_python_converter<Tango::DevEncoded, DevEncoded_to_tuple>();
    // bopy::to_python_converter<unsigned char, UChar_to_str>();

    convert_PySequence_to_CORBA_Sequence<Tango::DevVarCharArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarShortArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarLongArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarFloatArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarDoubleArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarUShortArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarULongArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarStringArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarLongStringArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarDoubleStringArray>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarLong64Array>();
    convert_PySequence_to_CORBA_Sequence<Tango::DevVarULong64Array>();

    convert_numpy_to_integer<Tango::DEV_UCHAR>();
    convert_numpy_to_integer<Tango::DEV_SHORT>();
    convert_numpy_to_integer<Tango::DEV_LONG>();
    convert_numpy_to_float<Tango::DEV_FLOAT>();
    convert_numpy_to_float<Tango::DEV_DOUBLE>();
    convert_numpy_to_integer<Tango::DEV_USHORT>();
    convert_numpy_to_integer<Tango::DEV_ULONG>();
    convert_numpy_to_integer<Tango::DEV_LONG64>();
    convert_numpy_to_integer<Tango::DEV_ULONG64>();

    StdString_from_python_str_unicode();

    // from tango_const.h
    export_poll_device();

    // from devapi.h
    export_locker_info();
    // TODO export_locking_thread();
    export_dev_command_info();
    export_attribute_dimension();
    export_command_info();
    export_device_info();
    export_device_attribute_config();
    export_attribute_info();
    export_attribute_alarm_info();
    export_change_event_info();
    export_periodic_event_info();
    export_archive_event_info();
    export_attribute_event_info();
    export_attribute_info_ex();
    export_device_data();
    export_device_attribute();
    export_device_data_history();
    export_device_attribute_history();
    export_device_pipe();
    export_pipe_info();

    export_dev_error();
    export_time_val();

    bopy::def("raise_asynch_exception", &raise_asynch_exception);

    bopy::def("_get_tango_lib_release", &Tango::_convert_tango_lib_release);

    export_coverage_helper();
}
