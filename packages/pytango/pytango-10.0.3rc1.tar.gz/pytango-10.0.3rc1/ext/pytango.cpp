/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#include "precompiled_header.hpp"

#define PY_ARRAY_UNIQUE_SYMBOL pytango_ARRAY_API
#include <numpy/arrayobject.h>

#include <tango/tango.h>

void export_version();
void export_enums();
void export_constants();
void export_base_types();
void export_event_data();
void export_attr_conf_event_data();
void export_data_ready_event_data();
void export_pipe_event_data();
void export_exceptions();
void export_api_util();
void export_connection();
void export_device_proxy();
void export_devintr_change_event_data();
void export_attribute_proxy();
void export_db();
void export_callback(); /// @todo not sure were to put it...
void export_util();
void export_pipe();
void export_attr();
void export_fwdattr();
void export_attribute();
void export_encoded_attribute();
void export_wattribute();
void export_multi_attribute();
void export_multi_class_attribute();
void export_user_default_attr_prop();
void export_user_default_fwdattr_prop();
void export_user_default_pipe_prop();
void export_sub_dev_diag();
void export_dserver();
void export_device_class();
void export_device_impl();
void export_group();
void export_log4tango();
void export_auto_tango_monitor();
void export_ensure_omni_thread();
void export_telemetry_helpers();

void *init_numpy(void)
{
    import_array();
    return NULL;
}

BOOST_PYTHON_MODULE(_tango)
{
    const bool show_user_defined = false;
    const bool show_py_signatures = false;

    bopy::docstring_options doc_opts(show_user_defined, show_py_signatures);

    init_numpy();

    export_callback(); /// @todo not sure were to put it...

    export_version();
    export_enums();
    export_constants();
    export_base_types();
    export_event_data();
    export_attr_conf_event_data();
    export_data_ready_event_data();
    export_pipe_event_data();
    export_devintr_change_event_data();
    export_exceptions();
    export_api_util();
    export_connection();
    export_device_proxy();
    export_attribute_proxy();
    export_db();
    export_util();
    export_pipe();
    export_attr();
    export_fwdattr();
    export_attribute();
    export_encoded_attribute();
    export_wattribute();
    export_multi_attribute();
    export_multi_class_attribute();
    export_user_default_attr_prop();
    export_user_default_fwdattr_prop();
    export_user_default_pipe_prop();
    export_sub_dev_diag();
    export_device_class();
    export_device_impl();
    //@warning export_dserver must be made after export_device_impl
    export_dserver();
    export_group();
    export_log4tango();
    export_auto_tango_monitor();
    export_ensure_omni_thread();
    export_telemetry_helpers();
}
