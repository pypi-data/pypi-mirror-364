# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is an internal PyTango module.
"""

__all__ = ("auto_monitor_init",)

__docformat__ = "restructuredtext"

from tango._tango import AutoTangoMonitor, AutoTangoAllowThreads


def __AutoTangoMonitor__enter__(self):
    self._acquire()
    return self


def __AutoTangoMonitor__exit__(self, *args, **kwargs):
    self._release()


def __init_AutoTangoMonitor():
    AutoTangoMonitor.__enter__ = __AutoTangoMonitor__enter__
    AutoTangoMonitor.__exit__ = __AutoTangoMonitor__exit__


def __doc_AutoTangoMonitor():
    AutoTangoMonitor.__doc__ = """\

    In a tango server, guard the tango monitor within a python context::

        with AutoTangoMonitor(dev):
            # code here is protected by the tango device monitor
            do something
    """


def __AutoTangoAllowThreads__enter__(self):
    return self


def __AutoTangoAllowThreads__exit__(self, *args, **kwargs):
    self._acquire()


def __init_AutoTangoAllowThreads():
    AutoTangoAllowThreads.__enter__ = __AutoTangoAllowThreads__enter__
    AutoTangoAllowThreads.__exit__ = __AutoTangoAllowThreads__exit__


def __doc_AutoTangoAllowThreads():
    AutoTangoAllowThreads.__doc__ = """\

    In a tango server, free the tango monitor within a context:

        with AutoTangoAllowThreads(dev):
            # code here is not under the tango device monitor
            do something
    """


def auto_monitor_init(doc=True):
    __init_AutoTangoMonitor()
    __init_AutoTangoAllowThreads()
    if doc:
        __doc_AutoTangoMonitor()
        __doc_AutoTangoAllowThreads()
