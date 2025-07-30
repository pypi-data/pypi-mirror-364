# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is an internal PyTango module.
"""

__all__ = ("init",)

__docformat__ = "restructuredtext"

import numpy

from tango.attribute_proxy import attribute_proxy_init
from tango.base_types import base_types_init
from tango.exception import exception_init
from tango.callback import callback_init
from tango.api_util import api_util_init
from tango.encoded_attribute import encoded_attribute_init
from tango.connection import connection_init
from tango.db import db_init
from tango.device_attribute import device_attribute_init
from tango.device_class import device_class_init
from tango.device_data import device_data_init
from tango.device_proxy import device_proxy_init
from tango.device_server import device_server_init
from tango.group import group_init
from tango.group_reply import group_reply_init
from tango.group_reply_list import group_reply_list_init
from tango.pytango_pprint import pytango_pprint_init
from tango.pyutil import pyutil_init
from tango.time_val import time_val_init
from tango.auto_monitor import auto_monitor_init
from tango.pipe import pipe_init
from tango._tango import constants
from tango._tango import _get_tango_lib_release

__INITIALIZED = False
__DOC = True


def init_constants():
    import sys
    import platform

    tg_ver = tuple(map(int, constants.TgLibVers.split(".")))
    tg_ver_str = "0x%02d%02d%02d00" % (tg_ver[0], tg_ver[1], tg_ver[2])
    constants.TANGO_VERSION_HEX = int(tg_ver_str, 16)

    BOOST_VERSION = ".".join(
        map(
            str,
            (
                constants.BOOST_MAJOR_VERSION,
                constants.BOOST_MINOR_VERSION,
                constants.BOOST_PATCH_VERSION,
            ),
        )
    )
    constants.BOOST_VERSION = BOOST_VERSION

    class Compile:
        PY_VERSION = constants.PY_VERSION
        TANGO_VERSION = constants.TANGO_VERSION
        BOOST_VERSION = constants.BOOST_VERSION
        NUMPY_VERSION = constants.NUMPY_VERSION
        # UNAME = tuple(map(str, json.loads(constants.UNAME)))

    tg_rt_ver_nb = _get_tango_lib_release()
    tg_rt_major_ver = tg_rt_ver_nb // 100
    tg_rt_minor_ver = tg_rt_ver_nb // 10 % 10
    tg_rt_patch_ver = tg_rt_ver_nb % 10
    tg_rt_ver = ".".join(map(str, (tg_rt_major_ver, tg_rt_minor_ver, tg_rt_patch_ver)))

    class Runtime:
        PY_VERSION = ".".join(map(str, sys.version_info[:3]))
        TANGO_VERSION = tg_rt_ver
        NUMPY_VERSION = numpy.__version__
        UNAME = platform.uname()

    constants.Compile = Compile
    constants.Runtime = Runtime


def init():
    global __INITIALIZED
    if __INITIALIZED:
        return

    global __DOC
    doc = __DOC
    init_constants()
    base_types_init(doc=doc)
    exception_init(doc=doc)
    callback_init(doc=doc)
    api_util_init(doc=doc)
    encoded_attribute_init(doc=doc)
    connection_init(doc=doc)
    db_init(doc=doc)
    device_attribute_init(doc=doc)
    device_class_init(doc=doc)
    device_data_init(doc=doc)
    device_proxy_init(doc=doc)
    device_server_init(doc=doc)
    group_init(doc=doc)
    group_reply_init(doc=doc)
    group_reply_list_init(doc=doc)
    pytango_pprint_init(doc=doc)
    pyutil_init(doc=doc)
    time_val_init(doc=doc)
    auto_monitor_init(doc=doc)
    pipe_init(doc=doc)

    # must come last: depends on device_proxy.init()
    attribute_proxy_init(doc=doc)

    __INITIALIZED = True
