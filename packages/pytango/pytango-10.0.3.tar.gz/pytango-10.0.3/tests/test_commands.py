# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
import numpy as np

try:
    import numpy.typing as npt
except ImportError:
    npt = None

import pytest

from tango import (
    DevFailed,
    DevState,
    GreenMode,
    PyTangoUserWarning,  # noqa
    DispLevel,
    DevVarDoubleArray,
    DevLong64,
    CommandInfoList,
)
from tango.server import Device
from tango.server import command
from tango.test_utils import DeviceTestContext
from tango.test_utils import (
    assert_close,
    general_decorator,
    general_asyncio_decorator,
    convert_dtype_to_typing_hint,
)


def test_identity_command(command_typed_values, server_green_mode):
    dtype, values, expected = command_typed_values

    if dtype == (bool,):
        pytest.xfail("Not supported for some reasons")

    if server_green_mode == GreenMode.Asyncio:

        class TestDevice(Device):
            green_mode = server_green_mode

            @command(dtype_in=dtype, dtype_out=dtype)
            async def identity(self, arg):
                return arg

    else:

        class TestDevice(Device):
            green_mode = server_green_mode

            @command(dtype_in=dtype, dtype_out=dtype)
            def identity(self, arg):
                return arg

    with DeviceTestContext(TestDevice) as proxy:
        for value in values:
            assert_close(proxy.identity(value), expected(value))


def test_identity_command_with_typing(command_typed_values):
    dtype, values, expected = command_typed_values
    tuple_hint, list_hint, _, _ = convert_dtype_to_typing_hint(dtype)

    if dtype == (bool,):
        pytest.xfail("Not supported for some reasons")

    class TestDevice(Device):
        @command()
        def command_tuple_hint(self, arg: tuple_hint) -> tuple_hint:
            return arg

        @command()
        def command_list_hint(self, arg: list_hint) -> list_hint:
            return arg

        @command(dtype_in=dtype, dtype_out=dtype)
        def command_user_type_has_priority(self, arg: dict) -> dict:
            return arg

    with DeviceTestContext(TestDevice) as proxy:
        for value in values:
            assert_close(proxy.command_tuple_hint(value), expected(value))
            assert_close(proxy.command_list_hint(value), expected(value))
            assert_close(proxy.command_user_type_has_priority(value), expected(value))


def test_devstate_command_with_typing():
    class TestDevice(Device):
        @command
        def arbitrary_devstate_command(self, arg_in: DevState) -> DevState:
            return arg_in

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.arbitrary_devstate_command(DevState.MOVING) == DevState.MOVING


def test_command_self_typed_with_not_defined_name():
    class TestDevice(Device):
        @command
        def identity(self: "TestDevice", arg_in: int) -> int:
            return arg_in

        def dynamic_identity(self: "TestDevice", arg_in: int) -> int:
            return arg_in

        @command()
        def add_dyn_cmd(self: "TestDevice"):
            cmd = command(f=self.dynamic_identity)
            self.add_command(cmd)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_cmd()
        assert 1 == proxy.identity(1)
        assert 1 == proxy.dynamic_identity(1)


def test_decorated_command(server_green_mode):
    if server_green_mode == GreenMode.Asyncio:

        class TestDevice(Device):
            green_mode = server_green_mode
            is_allowed = None

            @command(dtype_in=int, dtype_out=int)
            @general_asyncio_decorator()
            async def identity(self, arg):
                return arg

            @general_asyncio_decorator
            async def is_identity_allowed(self):
                return self.is_allowed

            @command(dtype_in=bool)
            async def make_allowed(self, yesno):
                self.is_allowed = yesno

    else:

        class TestDevice(Device):
            green_mode = server_green_mode
            is_allowed = None

            @command(dtype_in=int, dtype_out=int)
            @general_decorator()
            def identity(self, arg):
                return arg

            @general_decorator
            def is_identity_allowed(self):
                return self.is_allowed

            @command(dtype_in=bool)
            def make_allowed(self, yesno):
                self.is_allowed = yesno

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        assert_close(proxy.identity(123), 123)

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            proxy.identity(1)


def test_command_isallowed(server_green_mode):
    is_allowed = None

    def sync_allowed(device):
        assert isinstance(device, TestDevice)
        return is_allowed

    async def async_allowed(device):
        assert isinstance(device, TestDevice)
        return is_allowed

    class IsAllowedCallableClass:
        def __init__(self):
            self._is_allowed = None

        def __call__(self, device):
            assert isinstance(device, TestDevice)
            return self._is_allowed

        def make_allowed(self, yesno):
            self._is_allowed = yesno

    is_allowed_callable_class = IsAllowedCallableClass()

    class AsyncIsAllowedCallableClass(IsAllowedCallableClass):
        async def __call__(self, device):
            assert isinstance(device, TestDevice)
            return self._is_allowed

    async_is_allowed_callable_class = AsyncIsAllowedCallableClass()

    if server_green_mode == GreenMode.Asyncio:

        class TestDevice(Device):
            green_mode = server_green_mode

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._is_allowed = True

            @command(dtype_in=int, dtype_out=int)
            async def identity(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int, fisallowed="is_identity_allowed")
            async def identity_kwarg_string(self, arg):
                return arg

            @command(
                dtype_in=int,
                dtype_out=int,
                fisallowed=async_allowed,
            )
            async def identity_kwarg_callable(self, arg):
                return arg

            @command(
                dtype_in=int, dtype_out=int, fisallowed=async_is_allowed_callable_class
            )
            async def identity_kwarg_callable_class(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int)
            async def identity_always_allowed(self, arg):
                return arg

            @command(dtype_in=bool)
            async def make_allowed(self, yesno):
                self._is_allowed = yesno

            async def is_identity_allowed(self):
                return self._is_allowed

    else:

        class TestDevice(Device):
            green_mode = server_green_mode

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._is_allowed = True

            @command(dtype_in=int, dtype_out=int)
            def identity(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int, fisallowed="is_identity_allowed")
            def identity_kwarg_string(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int, fisallowed=sync_allowed)
            def identity_kwarg_callable(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int, fisallowed=is_allowed_callable_class)
            def identity_kwarg_callable_class(self, arg):
                return arg

            @command(dtype_in=int, dtype_out=int)
            def identity_always_allowed(self, arg):
                return arg

            @command(dtype_in=bool)
            def make_allowed(self, yesno):
                self._is_allowed = yesno

            def is_identity_allowed(self):
                return self._is_allowed

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        is_allowed_callable_class.make_allowed(True)
        async_is_allowed_callable_class.make_allowed(True)
        is_allowed = True

        assert_close(proxy.identity(1), 1)
        assert_close(proxy.identity_kwarg_string(1), 1)
        assert_close(proxy.identity_kwarg_callable(1), 1)
        assert_close(proxy.identity_kwarg_callable_class(1), 1)
        assert_close(proxy.identity_always_allowed(1), 1)

        proxy.make_allowed(False)
        is_allowed_callable_class.make_allowed(False)
        async_is_allowed_callable_class.make_allowed(False)
        is_allowed = False

        with pytest.raises(DevFailed):
            proxy.identity(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_string(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_class(1)

        assert_close(proxy.identity_always_allowed(1), 1)


@pytest.mark.parametrize("device_command_level", [True, False])
def test_dynamic_command(device_command_level, server_green_mode):
    is_allowed = None

    def sync_allowed(device):
        assert isinstance(device, TestDevice)
        return is_allowed

    async def async_allowed(device):
        assert isinstance(device, TestDevice)
        return is_allowed

    class IsAllowedCallable:
        def __init__(self):
            self._is_allowed = None

        def __call__(self, device):
            assert isinstance(device, TestDevice)
            return self._is_allowed

        def make_allowed(self, yesno):
            self._is_allowed = yesno

    class AsyncIsAllowedCallable(IsAllowedCallable):
        async def __call__(self, device):
            assert isinstance(device, TestDevice)
            return self._is_allowed

    is_allowed_callable_class = IsAllowedCallable()
    async_is_allowed_callable_class = AsyncIsAllowedCallable()

    class BaseTestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._is_allowed = True

        def _add_dyn_cmd(self):
            cmd = command(f=self.identity, dtype_in=int, dtype_out=int)
            self.add_command(cmd, device_command_level)

            cmd = command(
                f=self.identity_kwarg_string,
                dtype_in=int,
                dtype_out=int,
                fisallowed="is_identity_allowed",
            )
            self.add_command(cmd, device_command_level)

            cmd = command(
                f=self.identity_kwarg_callable,
                dtype_in=int,
                dtype_out=int,
                fisallowed=self.is_identity_allowed,
            )
            self.add_command(cmd, device_command_level)

            cmd = command(
                f=self.identity_kwarg_callable_outside_class,
                dtype_in=int,
                dtype_out=int,
                fisallowed=(
                    sync_allowed
                    if server_green_mode != GreenMode.Asyncio
                    else async_allowed
                ),
            )
            self.add_command(cmd, device_command_level)

            cmd = command(
                f=self.identity_kwarg_callable_class,
                dtype_in=int,
                dtype_out=int,
                fisallowed=(
                    is_allowed_callable_class
                    if server_green_mode != GreenMode.Asyncio
                    else async_is_allowed_callable_class
                ),
            )
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_always_allowed, dtype_in=int, dtype_out=int)
            self.add_command(cmd, device_command_level)

    if server_green_mode == GreenMode.Asyncio:

        class TestDevice(BaseTestDevice):
            async def identity(self, arg):
                return arg

            async def identity_kwarg_string(self, arg):
                return arg

            async def identity_kwarg_callable(self, arg):
                return arg

            async def identity_kwarg_callable_outside_class(self, arg):
                return arg

            async def identity_kwarg_callable_class(self, arg):
                return arg

            async def identity_always_allowed(self, arg):
                return arg

            @command()
            async def add_dyn_cmd(self):
                self._add_dyn_cmd()

            @command(dtype_in=bool)
            async def make_allowed(self, yesno):
                self._is_allowed = yesno

            async def is_identity_allowed(self):
                return self._is_allowed

    else:

        class TestDevice(BaseTestDevice):
            def identity(self, arg):
                return arg

            def identity_kwarg_string(self, arg):
                return arg

            def identity_kwarg_callable(self, arg):
                return arg

            def identity_kwarg_callable_outside_class(self, arg):
                return arg

            def identity_kwarg_callable_class(self, arg):
                return arg

            def identity_always_allowed(self, arg):
                return arg

            @command()
            def add_dyn_cmd(self):
                self._add_dyn_cmd()

            @command(dtype_in=bool)
            def make_allowed(self, yesno):
                self._is_allowed = yesno

            def is_identity_allowed(self):
                return self._is_allowed

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_cmd()

        proxy.make_allowed(True)
        is_allowed_callable_class.make_allowed(True)
        async_is_allowed_callable_class.make_allowed(True)
        is_allowed = True

        assert_close(proxy.identity(1), 1)
        assert_close(proxy.identity_kwarg_string(1), 1)
        assert_close(proxy.identity_kwarg_callable(1), 1)
        assert_close(proxy.identity_kwarg_callable_outside_class(1), 1)
        assert_close(proxy.identity_kwarg_callable_class(1), 1)
        assert_close(proxy.identity_always_allowed(1), 1)

        proxy.make_allowed(False)
        is_allowed_callable_class.make_allowed(False)
        async_is_allowed_callable_class.make_allowed(False)
        is_allowed = False

        with pytest.raises(DevFailed):
            proxy.identity(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_string(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_outside_class(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_class(1)

        assert_close(proxy.identity_always_allowed(1), 1)


def test_identity_dynamic_command_with_typing(command_typed_values):
    dtype, values, expected = command_typed_values
    tuple_hint, list_hint, _, _ = convert_dtype_to_typing_hint(dtype)

    if dtype == (bool,):
        pytest.xfail("Not supported for some reasons")

    class TestDevice(Device):
        def command_tuple_hint(self, arg: tuple_hint) -> tuple_hint:
            return arg

        def command_list_hint(self, arg: list_hint) -> list_hint:
            return arg

        def command_user_type_has_priority(self, arg: dict) -> dict:
            return arg

        @command()
        def add_dyn_cmd(self):
            cmd = command(f=self.command_tuple_hint)
            self.add_command(cmd)

            cmd = command(f=self.command_list_hint)
            self.add_command(cmd)

            cmd = command(
                f=self.command_user_type_has_priority, dtype_in=dtype, dtype_out=dtype
            )
            self.add_command(cmd)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_cmd()
        for value in values:
            assert_close(proxy.command_tuple_hint(value), expected(value))
            assert_close(proxy.command_list_hint(value), expected(value))
            assert_close(proxy.command_user_type_has_priority(value), expected(value))


if npt:

    def test_identity_commands_with_numpy_typing(command_numpy_typed_values):
        type_hint, dformat, value, expected = command_numpy_typed_values
        if type_hint == np.uint8:
            pytest.xfail("Does not work for some reason")

        class TestDevice(Device):
            def identity_dynamic_command(self, arg: type_hint) -> type_hint:
                return arg

            @command
            def identity_static_command(self, arg: type_hint) -> type_hint:
                return arg

            @command()
            def add_dyn_cmd(self):
                cmd = command(f=self.identity_dynamic_command)
                self.add_command(cmd)

        with DeviceTestContext(TestDevice) as proxy:
            proxy.add_dyn_cmd()
            assert_close(proxy.identity_static_command(value), expected(value))
            assert_close(proxy.identity_dynamic_command(value), expected(value))


def test_polled_command():
    dct = {"Polling1": 100, "Polling2": 100000, "Polling3": 500}

    class TestDevice(Device):

        @command(polling_period=dct["Polling1"])
        def Polling1(self):
            pass

        @command(polling_period=dct["Polling2"])
        def Polling2(self):
            pass

        @command(polling_period=dct["Polling3"])
        def Polling3(self):
            pass

    with DeviceTestContext(TestDevice) as proxy:
        ans = proxy.polling_status()

    for info in ans:
        lines = info.split("\n")
        comm = lines[0].split("= ")[1]
        period = int(lines[1].split("= ")[1])
        assert dct[comm] == period


def test_wrong_command_result():
    class TestDevice(Device):

        @command(dtype_out=str)
        def cmd_str_err(self):
            return 1.2345

        @command(dtype_out=int)
        def cmd_int_err(self):
            return "bla"

        @command(dtype_out=[str])
        def cmd_str_list_err(self):
            return ["hello", 55]

    with DeviceTestContext(TestDevice) as proxy:
        with pytest.raises(DevFailed):
            proxy.cmd_str_err()
        with pytest.raises(DevFailed):
            proxy.cmd_int_err()
        with pytest.raises(DevFailed):
            proxy.cmd_str_list_err()


def test_command_info():
    class TestDevice(Device):

        @command(
            doc_in="identity_scalar doc_in",
            doc_out="identity_scalar doc_out",
            display_level=DispLevel.OPERATOR,
        )
        def identity_scalar(self, val: int) -> int:
            return val

        @command(
            doc_in="identity_spectrum doc_in",
            doc_out="identity_spectrum doc_out",
            display_level=DispLevel.EXPERT,
        )
        def identity_spectrum(self, val: list[float]) -> list[float]:
            return val

    with DeviceTestContext(TestDevice) as proxy:
        info = proxy.get_command_config("identity_scalar")
        assert info.cmd_name == "identity_scalar"
        assert info.disp_level == DispLevel.OPERATOR
        assert info.in_type == DevLong64
        assert info.in_type_desc == "identity_scalar doc_in"
        assert info.out_type == DevLong64
        assert info.out_type_desc == "identity_scalar doc_out"

        info = proxy.get_command_config()
        assert isinstance(info, CommandInfoList)
        assert len(info) == 5
        assert info[3].cmd_name == "identity_scalar"
        assert info[3].disp_level == DispLevel.OPERATOR
        assert info[3].in_type == DevLong64
        assert info[3].in_type_desc == "identity_scalar doc_in"
        assert info[3].out_type == DevLong64
        assert info[3].out_type_desc == "identity_scalar doc_out"

        assert info[4].cmd_name == "identity_spectrum"
        assert info[4].disp_level == DispLevel.EXPERT
        assert info[4].in_type == DevVarDoubleArray
        assert info[4].in_type_desc == "identity_spectrum doc_in"
        assert info[4].out_type == DevVarDoubleArray
        assert info[4].out_type_desc == "identity_spectrum doc_out"
