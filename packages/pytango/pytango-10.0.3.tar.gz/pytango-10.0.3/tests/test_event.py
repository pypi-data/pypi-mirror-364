# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
# Imports

import time
import sys
import gevent

from threading import Thread

import pytest
from io import StringIO

from tango import (
    EventType,
    GreenMode,
    AttrQuality,
    DevFailed,
    EnsureOmniThread,
    is_omni_thread,
)

from tango._tango import Except
from tango.server import Device
from tango.server import command, attribute
from tango.test_utils import DeviceTestContext, assert_close
from tango.utils import EventCallback, AsyncEventCallback


MAX_RETRIES = 200
DELAY_PER_RETRY = 0.05

event_results = []


async def async_callback(evt):
    event_callback(evt)


def event_callback(evt):
    if evt.err:
        event_results.append(evt.errors[0].desc)
    elif hasattr(evt, "ctr"):
        event_results.append(evt.ctr)
    elif hasattr(evt, "attr_value"):
        event_results.append(evt.attr_value.value)
    else:
        event_results.append(evt)


# Test device
class EventDevice(Device):
    _requested_event_type = None
    _base = 0

    def init_device(self):
        self.set_change_event("attr", True, False)
        # even if set_alarm_event is not necessary after we did set_change_event,
        # we call it to test that function works
        self.set_alarm_event("attr", True, False)
        self.set_data_ready_event("attr", True)
        self.set_archive_event("attr", True, False)

    @attribute()
    def attr(self) -> int:
        # to avoid sending events at subscription
        if self._requested_event_type is not None:
            self._base += 10
            self._send_events(self._requested_event_type)
        return 0

    @attr.write
    def attr(self, event_type):
        self._base += 10
        self._requested_event_type = event_type
        self._send_events(event_type)

    @command
    def reset(self):
        self._requested_event_type = None
        self._base = 0

    def _send_events(self, event_type: int):
        # to test fire_xxx_event methods we should have attr object and exception, converted to DevFailed:
        attr = self.get_device_attr().get_attr_by_name("attr")
        try:
            raise Exception(f"test exception {self._base + 1}")
        except Exception:
            test_exception = Except.to_dev_failed(*sys.exc_info())

        if event_type == EventType.USER_EVENT:
            self.push_event("attr", [], [], self._base + 1)
            self.push_event(
                "attr", [], [], self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )
            self.push_event("attr", [], [], Exception(f"test exception {self._base}"))

        elif event_type == EventType.ARCHIVE_EVENT:
            self.push_archive_event("attr", self._base + 1)
            self.push_archive_event(
                "attr", self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )
            self.push_archive_event("attr", Exception(f"test exception {self._base}"))

        elif event_type == EventType.CHANGE_EVENT:
            self.push_change_event("attr", self._base + 1)

            self.push_change_event(
                "attr", self._base + 2, 3.0, AttrQuality.ATTR_WARNING
            )

            attr.set_value(self._base + 3)
            attr.fire_change_event()

            self.push_change_event("attr", Exception(f"test exception {self._base}"))

            attr.fire_change_event(test_exception)

        elif event_type == EventType.ALARM_EVENT:
            self.push_alarm_event("attr", self._base + 1)

            self.push_alarm_event("attr", self._base + 2, 3.0, AttrQuality.ATTR_WARNING)

            attr.set_value(self._base + 3)
            attr.fire_alarm_event()

            self.push_alarm_event("attr", Exception(f"test exception {self._base}"))

            attr.fire_alarm_event(test_exception)

        elif event_type == EventType.DATA_READY_EVENT:
            self.push_data_ready_event("attr", self._base + 1)

    @command
    def send_events(self, event_type: int):
        self._send_events(event_type)

    @command
    def send_event_no_data(self, attr_name: str):
        self.push_event(attr_name, [], [])

    @command
    def send_archive_event_no_data(self, attr_name: str):
        self.push_archive_event(attr_name)

    @command
    def send_change_event_no_data(self, attr_name: str):
        self.push_change_event(attr_name)

    @command
    def send_alarm_event_no_data(self, attr_name: str):
        self.push_alarm_event(attr_name)

    @command(dtype_in=str)
    def add_dyn_attr(self, name):
        attr = attribute(name=name, dtype="float", fget=self.read)
        self.add_attribute(attr)

    @command(dtype_in=str)
    def delete_dyn_attr(self, name):
        self.remove_attribute(name)

    def read(self, attr):
        attr.set_value(1.23)


cmd_list = {
    "Init",
    "State",
    "Status",
    "reset",
    "add_dyn_attr",
    "delete_dyn_attr",
    "send_events",
    "send_event_no_data",
    "send_archive_event_no_data",
    "send_change_event_no_data",
    "send_alarm_event_no_data",
}

attr_list = {"attr", "State", "Status"}


# Device fixture
@pytest.fixture(scope="module")
def event_device(green_mode_device_proxy):
    context = DeviceTestContext(EventDevice, host="127.0.0.1", process=True)
    with context:
        yield green_mode_device_proxy(context.get_device_access())


# Tests
def assert_events_received(event_device, expected_res):
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(event_results) >= len(expected_res):
            assert_close(event_results, expected_res)
            return
        time.sleep(DELAY_PER_RETRY)
    timeout_seconds = MAX_RETRIES * DELAY_PER_RETRY
    pytest.fail(
        f"Timeout, waiting for event, after {timeout_seconds} sec over {MAX_RETRIES} retries. "
        f"Occasionally happens, probably due to CI test runtime environment"
    )


def run_event_test(event_device, event_type, cb, expected_res):
    event_results.clear()
    event_device.command_inout("reset", wait=True)

    eid_change = event_device.subscribe_event("attr", event_type, cb, wait=True)

    # Trigger events from command
    event_device.command_inout("send_events", event_type, wait=True)

    # Trigger events from attribute write method
    event_device.write_attribute("attr", event_type, wait=True)

    # Trigger events from attribute read method
    event_device.read_attribute("attr", wait=True)

    # Test the event values
    assert_events_received(event_device, expected_res)

    # Unsubscribe
    event_device.unsubscribe_event(eid_change)


def test_change_event(event_device):
    expected_res = [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
        11,
        12,
        13,
        "Exception: test exception 10\n",
        "Exception: test exception 11\n",
        21,
        22,
        23,
        "Exception: test exception 20\n",
        "Exception: test exception 21\n",
    ]

    if event_device.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device,
            EventType.CHANGE_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device,
                EventType.CHANGE_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device,
            EventType.CHANGE_EVENT,
            event_callback,
            expected_res,
        )


def test_alarm_event(event_device):
    expected_res = [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
        11,
        12,
        13,
        "Exception: test exception 10\n",
        "Exception: test exception 11\n",
        21,
        22,
        23,
        "Exception: test exception 20\n",
        "Exception: test exception 21\n",
    ]

    if event_device.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device,
            EventType.ALARM_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device,
                EventType.ALARM_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device,
            EventType.ALARM_EVENT,
            event_callback,
            expected_res,
        )


def test_user_event(event_device):
    expected_res = [
        0,
        1,
        2,
        "Exception: test exception 0\n",
        11,
        12,
        "Exception: test exception 10\n",
        21,
        22,
        "Exception: test exception 20\n",
    ]

    if event_device.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device,
            EventType.USER_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device,
                EventType.USER_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device,
            EventType.USER_EVENT,
            event_callback,
            expected_res,
        )


def test_archive_event(event_device):
    expected_res = [
        0,
        1,
        2,
        "Exception: test exception 0\n",
        11,
        12,
        "Exception: test exception 10\n",
        21,
        22,
        "Exception: test exception 20\n",
    ]

    if event_device.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device,
            EventType.ARCHIVE_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device,
                EventType.ARCHIVE_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device,
            EventType.ARCHIVE_EVENT,
            event_callback,
            expected_res,
        )


def test_subscribe_data_ready_event(event_device):
    expected_res = [1, 11, 21]
    if event_device.get_green_mode() == GreenMode.Asyncio:
        run_event_test(
            event_device,
            EventType.DATA_READY_EVENT,
            async_callback,
            expected_res,
        )
        with pytest.warns(DeprecationWarning):
            run_event_test(
                event_device,
                EventType.DATA_READY_EVENT,
                event_callback,
                expected_res,
            )
    else:
        run_event_test(
            event_device,
            EventType.DATA_READY_EVENT,
            event_callback,
            expected_res,
        )


def __test_interface_event(event_device, cb):
    event_results.clear()

    # Subscribe
    eid = event_device.subscribe_event(
        "attr", EventType.INTERFACE_CHANGE_EVENT, cb, wait=True
    )
    # Trigger an event
    event_device.command_inout("add_dyn_attr", "bla", wait=True)
    event_device.read_attribute("bla", wait=True)
    # Wait for tango event
    assert_events_received(event_device, [True, True])

    event_device.command_inout("delete_dyn_attr", "bla", wait=True)
    # Wait for tango event
    assert_events_received(event_device, [True, True, True])
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_subscribe_interface_event(event_device):
    def __check_event(event):
        if len(event_results) == 0:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list
        elif len(event_results) == 1:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list | {"bla"}
        else:
            assert {cmd.cmd_name for cmd in event.cmd_list} == cmd_list
            assert {att.name for att in event.att_list} == attr_list

        event_results.append(True)

    async def async_interface_callback(evt):
        __check_event(evt)

    def interface_callback(evt):
        __check_event(evt)

    if event_device.get_green_mode() == GreenMode.Asyncio:
        __test_interface_event(event_device, async_interface_callback)
        with pytest.warns(DeprecationWarning):
            __test_interface_event(event_device, interface_callback)
    else:
        __test_interface_event(event_device, interface_callback)


def __test_push_event_with_timestamp(event_device, cb, string):
    # to reduce tests amount here we test only change event
    eid = event_device.subscribe_event("attr", EventType.CHANGE_EVENT, cb, wait=True)
    # trigger an event
    event_device.command_inout("send_events", EventType.CHANGE_EVENT, wait=True)
    # wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(cb.get_events()) > 5:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
            f"Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values and timestamp
    events = cb.get_events()
    results = [evt.attr_value.value for evt in events[:4]]
    assert results == [0, 1, 2, 3]
    assert events[2].attr_value.time.totime() == 3.0
    assert events[4].errors[0].desc == "Exception: test exception 0\n"
    assert events[5].errors[0].desc == "Exception: test exception 1\n"

    # Check string
    for line in [
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_VALID] 0",
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_VALID] 1",
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_WARNING] 2",
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_VALID] 3",
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [PyDs_PythonError] Exception: test exception 0",
        "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [PyDs_PythonError] Exception: test exception 1",
    ]:
        assert line in string.getvalue()
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_push_event_with_event_callback(event_device):
    string = StringIO()
    ec = EventCallback(fd=string)

    if event_device.get_green_mode() == GreenMode.Asyncio:
        with pytest.warns(DeprecationWarning):
            __test_push_event_with_timestamp(event_device, ec, string)
        string = StringIO()
        ec = AsyncEventCallback(fd=string)
        __test_push_event_with_timestamp(event_device, ec, string)
    else:
        __test_push_event_with_timestamp(event_device, ec, string)


def test_send_events_no_data(event_device):
    event_device.command_inout("send_event_no_data", "state", wait=True)
    event_device.command_inout("send_archive_event_no_data", "state", wait=True)
    event_device.command_inout("send_change_event_no_data", "state", wait=True)
    event_device.command_inout("send_alarm_event_no_data", "state", wait=True)

    event_device.command_inout("send_event_no_data", "status", wait=True)
    event_device.command_inout("send_archive_event_no_data", "status", wait=True)
    event_device.command_inout("send_change_event_no_data", "status", wait=True)
    with pytest.raises(
        DevFailed,
        match="without data parameter is only allowed for state attribute",
    ):
        event_device.command_inout("send_alarm_event_no_data", "status", wait=True)

    with pytest.raises(
        DevFailed,
        match="without data parameter is only allowed for state and status attributes",
    ):
        event_device.command_inout("send_event_no_data", "attr", wait=True)

    with pytest.raises(
        DevFailed,
        match="without data parameter is only allowed for state and status attributes",
    ):
        event_device.command_inout("send_archive_event_no_data", "attr", wait=True)

    with pytest.raises(
        DevFailed,
        match="without data parameter is only allowed for state and status attributes",
    ):
        event_device.command_inout("send_change_event_no_data", "attr", wait=True)

    with pytest.raises(
        DevFailed,
        match="without data parameter is only allowed for state and status attributes",
    ):
        event_device.command_inout("send_change_event_no_data", "attr", wait=True)


def test_main_thread_is_omni_thread():
    assert is_omni_thread()


def test_ensure_omni_thread_main_thread_is_omni_thread():
    with EnsureOmniThread():
        assert is_omni_thread()


def test_user_thread_is_not_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is False


def test_ensure_omni_thread_user_thread_is_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        with EnsureOmniThread():
            thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is True


def test_subscribe_change_event_from_user_thread(event_device):
    event_results.clear()

    def thread_func():
        with EnsureOmniThread():
            if event_device.get_green_mode() == GreenMode.Asyncio:
                eid = event_device.subscribe_event(
                    "attr", EventType.CHANGE_EVENT, async_callback, wait=True
                )
            else:
                eid = event_device.subscribe_event(
                    "attr", EventType.CHANGE_EVENT, event_callback, wait=True
                )
            while running:
                time.sleep(DELAY_PER_RETRY)
            event_device.unsubscribe_event(eid)

    # Start the thread
    thread = Thread(target=thread_func)
    running = True
    thread.start()
    # Wait for tango events
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(event_results) == 1:
            # Trigger an event (1 result means thread has completed subscription,
            # as that results in an initial callback)
            event_device.command_inout("send_events", EventType.CHANGE_EVENT, wait=True)
        elif len(event_results) > 2:
            # At least 2 events means an event was received after subscription
            break
        time.sleep(DELAY_PER_RETRY)
    # Stop the thread
    running = False

    # For gevent, we need to yield control for a short time in case the unsubscribe call's
    # greenlet hasn't completed yet. Otherwise, we get a deadlock on join.
    if event_device.get_green_mode() == GreenMode.Gevent:
        gevent.sleep(0.1)

    thread.join()
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
            f"Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values
    assert event_results == [
        0,
        1,
        2,
        3,
        "Exception: test exception 0\n",
        "Exception: test exception 1\n",
    ]


def test_get_events(event_device):
    for receiver in ["cb", "no"]:
        for event_type in EventType.values.values():
            event_results.clear()

            if event_type in [
                EventType.PERIODIC_EVENT,  # needs polling
                EventType.PIPE_EVENT,
            ]:  # obviously cannot be tested without pipes
                continue
            eid = event_device.subscribe_event("attr", event_type, 1, wait=True)

            # DATA_READY_EVENT does not send automatically at the subscription
            if event_type == EventType.DATA_READY_EVENT:
                event_device.send_events(event_type, wait=True)

            for retry_count in range(MAX_RETRIES):
                if receiver == "no":
                    if len(event_device.get_events(eid)):
                        break
                else:
                    event_device.get_events(eid, event_callback)
                    if len(event_results):
                        break
                time.sleep(DELAY_PER_RETRY)

            if retry_count + 1 >= MAX_RETRIES:
                timeout_seconds = retry_count * DELAY_PER_RETRY
                pytest.fail(
                    f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. "
                    f"Occasionally happens, probably due to CI test runtime environment"
                )

            event_device.unsubscribe_event(eid)
