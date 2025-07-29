import ctypes
import os
import warnings
import platform
import time
import typing

import numpy as np
import numpy.ctypeslib as npc

from .error_list import ERROR_STRING
from .constants import *


class PicoSDKNotFoundException(Exception):
    pass


class PicoSDKException(Exception):
    pass


class OverrangeWarning(UserWarning):
    pass


class PowerSupplyWarning(UserWarning):
    pass


# General Functions
def _check_path(location:str, folders:list) -> str:
    """Checks a list of folders in a location i.e. ['Pico Technology']
       in /ProgramFiles/ and returns first full path found

    Args:
        location (str): Path to check for folders
        folders (list): List of folders to look for

    Raises:
        PicoSDKException: If not found, raise an error for user

    Returns:
        str: Full path of the first located folder
    """
    for folder in folders:
        path = os.path.join(location, folder)
        if os.path.exists(path):
            return path
    raise PicoSDKException(
        "No PicoSDK or PicoScope 7 drivers installed, get them from http://picotech.com/downloads"
    )


def _get_lib_path() -> str:
    """Looks for PicoSDK folder based on OS and returns folder
       path

    Raises:
        PicoSDKException: If unsupported OS

    Returns:
        str: Full path of PicoSDK folder location
    """
    system = platform.system()
    if system == "Windows":
        program_files = os.environ.get("PROGRAMFILES")
        checklist = [
            'Pico Technology\\SDK\\lib',
            'Pico Technology\\PicoScope 7 T&M Stable',
            'Pico Technology\\PicoScope 7 T&M Early Access'
        ]
        return _check_path(program_files, checklist)
    elif system == "Linux":
        return _check_path('opt', 'picoscope')
    elif system == "Darwin":
        raise PicoSDKException("macOS is not yet tested and supported")
    else:
        raise PicoSDKException("Unsupported OS")
    
def _struct_to_dict(struct_instance: ctypes.Structure, format=False) -> dict:
    """Takes a ctypes struct and returns the values as a python dict

    Args:
        struct_instance (ctypes.Structure): ctype structure to convert into dictionary

    Returns:
        dict: python dictionary of struct values
    """
    result = {}
    for field_name, _ in struct_instance._fields_:
        if format:
            result[field_name.replace('_', '')] = getattr(struct_instance, field_name)
        else:
            result[field_name] = getattr(struct_instance, field_name)
    return result

class PicoScopeBase:
    """PicoScope base class including common SDK and python modules and functions"""
    # Class Functions
    def __init__(self, dll_name, *args, **kwargs):
        # Pytest override
        self._pytest = "pytest" in args
            
        # Setup DLL location per device
        if self._pytest:
            self.dll = None
        else:
            self.dll = ctypes.CDLL(os.path.join(_get_lib_path(), dll_name + ".dll"))
        self._unit_prefix_n = dll_name

        # Setup class variables
        self.handle = ctypes.c_short()
        self.range = {}
        self.probe_scale = {}
        self.resolution = None
        self.max_adc_value = None
        self.min_adc_value = None
        self.over_range = 0
    
    def __exit__(self):
        self.close_unit()

    def __del__(self):
        self.close_unit()

    # General Functions
    def _get_attr_function(self, function_name: str) -> ctypes.CDLL:
        """
        Returns ctypes function based on sub-class prefix name.

        For example, `_get_attr_function("OpenUnit")` will return `self.dll.ps####aOpenUnit()`.

        Args:
            function_name (str): PicoSDK function name, e.g., "OpenUnit".

        Returns:
            ctypes.CDLL: CDLL function for the specified name.
        """
        return getattr(self.dll, self._unit_prefix_n + function_name)
    
    def _error_handler(self, status: int) -> None:
        """
        Checks status code against error list; raises an exception if not 0.

        Errors such as `SUPPLY_NOT_CONNECTED` are returned as warnings.

        Args:
            status (int): Returned status value from PicoSDK.

        Raises:
            PicoSDKException: Pythonic exception based on status value.
        """
        error_code = ERROR_STRING[status]
        if status != 0:
            if status in [POWER_SOURCE.SUPPLY_NOT_CONNECTED]:
                warnings.warn('Power supply not connected.',
                              PowerSupplyWarning)
                return
            # Certain status codes indicate that the driver is busy or waiting
            # for more data rather than an actual failure. These should not
            # raise an exception as callers may poll until data is ready.
            if status == 407:  # PICO_WAITING_FOR_DATA_BUFFERS
                return
            # Streaming related status codes indicate no new data is ready.
            # These should not be treated as fatal errors and simply signal
            # the caller to try again later.
            if status in [28672, 28673, 28674]:
                return
            self.close_unit()
            raise PicoSDKException(error_code)
        return
    
    def _call_attr_function(self, function_name:str, *args) -> int:
        """
        Calls a specific attribute function with the provided arguments.

        Args:
            function_name (str): PicoSDK function suffix.

        Returns:
            int: Returns status integer of PicoSDK dll.
        """
        attr_function = self._get_attr_function(function_name)
        status = attr_function(*args)
        self._error_handler(status)
        return status

    # General PicoSDK functions    
    def _open_unit(self, serial_number:int=None, resolution:RESOLUTION=0) -> None:
        """
        Opens PicoScope unit.

        Args:
            serial_number (int, optional): Serial number of specific unit, e.g., JR628/0017.
            resolution (RESOLUTION, optional): Resolution of device. 
        """

        if serial_number is not None:
            serial_number = serial_number.encode()
        self._call_attr_function(
            'OpenUnit',
            ctypes.byref(self.handle),
            serial_number, 
            resolution
        )
        self.resolution = resolution
        self.set_all_channels_off()
    
    def close_unit(self) -> None:
        """
        Closes the PicoScope device and releases the hardware handle.

        This calls the PicoSDK `CloseUnit` function to properly disconnect from the device.

        Returns:
                None
        """
        if self._pytest:
            return
        else:
            self._get_attr_function('CloseUnit')(self.handle)

    def stop(self) -> None: 
        """
        This function stops the scope device from sampling data
        """
        self._call_attr_function(
            'Stop',
            self.handle
        )

    def is_ready(self) -> None:
        """
        Blocks execution until the PicoScope device is ready.

        Continuously calls the PicoSDK `IsReady` function in a loop, checking if
        the device is prepared to proceed with data acquisition.

        Returns:
                None
        """

        ready = ctypes.c_int16()
        attr_function = getattr(self.dll, self._unit_prefix_n + "IsReady")
        while True:
            status = attr_function(
                self.handle, 
                ctypes.byref(ready)
            )
            self._error_handler(status)
            if ready.value != 0:
                break
    
    # Get information from PicoScope
    def get_unit_info(self, unit_info: UNIT_INFO) -> str:
        """
        Get specified information from unit. Use UNIT_INFO.XXXX or integer.

        Args:
            unit_info (UNIT_INFO): Specify information from PicoScope unit i.e. UNIT_INFO.PICO_BATCH_AND_SERIAL.

        Returns:
            str: Returns data from device.
        """
        string = ctypes.create_string_buffer(16)
        string_length = ctypes.c_int16(32)
        required_size = ctypes.c_int16(32)
        status = self._call_attr_function(
            'GetUnitInfo',
            self.handle,
            string,
            string_length,
            ctypes.byref(required_size),
            ctypes.c_uint32(unit_info)
        )
        return string.value.decode()
    
    def get_unit_serial(self) -> str:
        """
        Get and return batch and serial of unit.

        Returns:
                str: Returns serial, e.g., "JR628/0017".
        """
        return self.get_unit_info(UNIT_INFO.PICO_BATCH_AND_SERIAL)

    def get_accessory_info(self, channel: CHANNEL, info: UNIT_INFO) -> str:
        """Return accessory details for the given channel.
        This wraps the driver ``GetAccessoryInfo`` call which retrieves
        information about any accessory attached to ``channel``.
        Args:
            channel: Channel the accessory is connected to.
            info: Information field requested from :class:`UNIT_INFO`.
        Returns:
            str: Information string provided by the driver.
        """

        string = ctypes.create_string_buffer(16)
        string_length = ctypes.c_int16(32)
        required_size = ctypes.c_int16(32)

        self._call_attr_function(
            "GetAccessoryInfo",
            self.handle,
            channel,
            string,
            string_length,
            ctypes.byref(required_size),
            ctypes.c_uint32(info),
        )

        return string.value.decode()
    
    def get_accessory_info(self, channel: CHANNEL, info: UNIT_INFO) -> str:
        """Return accessory details for the given channel.
        This wraps the driver ``GetAccessoryInfo`` call which retrieves
        information about any accessory attached to ``channel``.
        Args:
            channel: Channel the accessory is connected to.
            info: Information field requested from :class:`UNIT_INFO`.
        Returns:
            str: Information string provided by the driver.
        """

        string = ctypes.create_string_buffer(16)
        string_length = ctypes.c_int16(32)
        required_size = ctypes.c_int16(32)

        self._call_attr_function(
            "GetAccessoryInfo",
            self.handle,
            channel,
            string,
            string_length,
            ctypes.byref(required_size),
            ctypes.c_uint32(info),
        )

        return string.value.decode()
    
    def _get_enabled_channel_flags(self) -> int:
        """
        Returns integer of enabled channels as a binary code.
        Where channel A is LSB.
        I.e. Channel A and channel C would be '0101' -> 5

        Returns:
            int: Decimal of enabled channels
        """
        enabled_channel_byte = 0
        for channel in self.range:
            enabled_channel_byte += 2**channel
        return enabled_channel_byte
    
    def get_nearest_sampling_interval(self, interval_s:float) -> dict:
        """
        This function returns the nearest possible sample interval to the requested 
        sample interval. It does not change the configuration of the oscilloscope.

        Channels need to be setup first before calculating as more channels may 
        increase sample interval.

        Args:
            interval_s (float): Time value in seconds (s) you would like to obtain.

        Returns:
            dict: Dictionary of suggested timebase and actual sample interval in seconds (s).
        """
        timebase = ctypes.c_uint32()
        time_interval = ctypes.c_double()
        self._call_attr_function(
            'NearestSampleIntervalStateless',
            self.handle,
            self._get_enabled_channel_flags(),
            ctypes.c_double(interval_s),
            self.resolution,
            ctypes.byref(timebase),
            ctypes.byref(time_interval),
        )
        return {"timebase": timebase.value, "actual_sample_interval": time_interval.value}
    
    def get_timebase(timebase, samples):
        # Override for PicoScopeBase
        raise NotImplementedError("Method not yet available for this oscilloscope")
    
    def _get_timebase(self, timebase: int, samples: int, segment:int=0) -> dict:
        """
        This function calculates the sampling rate and maximum number of 
        samples for a given timebase under the specified conditions.

        Args:
                timebase (int): Selected timebase multiplier (refer to programmer's guide).
                samples (int): Number of samples.
                segment (int, optional): The index of the memory segment to use.

        Returns:
                dict: Returns interval (ns) and max samples as a dictionary.
        """
        time_interval_ns = ctypes.c_double()
        max_samples = ctypes.c_uint64()
        attr_function = getattr(self.dll, self._unit_prefix_n + 'GetTimebase')
        status = attr_function(
            self.handle,
            timebase,
            samples,
            ctypes.byref(time_interval_ns),
            ctypes.byref(max_samples),
            segment
        )
        self._error_handler(status)
        return {"Interval(ns)": time_interval_ns.value, 
                "Samples":          max_samples.value}
    
    def _get_timebase_2(self, timebase: int, samples: int, segment:int=0):
        """
        Calculates the sampling rate and maximum number of samples for a given
        timebase under the specified conditions.

        Args:
                timebase (int): Selected timebase multiplier (refer to programmer's guide).
                samples (int): Number of samples.
                segment (int, optional): Index of the memory segment to use.

        Returns:
                dict: Dictionary containing:
                        - 'interval' (ns): Time interval between samples.
                        - 'max_samples': Maximum number of samples.
        """
        time_interval_ns = ctypes.c_float()
        max_samples = ctypes.c_int32()
        attr_function = getattr(self.dll, self._unit_prefix_n + 'GetTimeBase2')
        status = attr_function(
            self.handle,
            timebase,
            samples,
            ctypes.byref(time_interval_ns),
            ctypes.byref(max_samples),
            segment
        )
        self._error_handler(status)
        return {"Interval(ns)": time_interval_ns.value, 
                "Samples":          max_samples.value}
    
    def sample_rate_to_timebase(self, sample_rate:float, unit=SAMPLE_RATE.MSPS):
        """
        Converts sample rate to a PicoScope timebase value based on the 
        attached PicoScope.

        This function will return the closest possible timebase.
        Use `get_nearest_sample_interval(interval_s)` to get the full timebase and 
        actual interval achieved.

        Args:
            sample_rate (int): Desired sample rate 
            unit (SAMPLE_RATE): unit of sample rate.
        """
        interval_s = 1 / (sample_rate * unit)
        
        return self.get_nearest_sampling_interval(interval_s)["timebase"]
    
    def interval_to_timebase(self, interval:float, unit=TIME_UNIT.S):
        """
        Converts a time interval (between samples) into a PicoScope timebase 
        value based on the attached PicoScope.

        This function will return the closest possible timebase.
        Use `get_nearest_sample_interval(interval_s)` to get the full timebase and 
        actual interval achieved.

        Args:
            interval (float): Desired time interval between samples
            unit (TIME_UNIT, optional): Time unit of interval.
        """
        interval_s = interval / unit
        return self.get_nearest_sampling_interval(interval_s)["timebase"]
    
    def _get_adc_limits(self) -> tuple:
        """
        Gets the ADC limits for specified devices.

        Currently tested on: 6000a.

        Returns:
                tuple: (minimum value, maximum value)

        Raises:
                PicoSDKException: If device hasn't been initialized.
        """
        if self.resolution is None:
            raise PicoSDKException("Device has not been initialized, use open_unit()")
        min_value = ctypes.c_int32()
        max_value = ctypes.c_int32()
        self._call_attr_function(
            'GetAdcLimits',
            self.handle,
            self.resolution,
            ctypes.byref(min_value),
            ctypes.byref(max_value)
        )
        return min_value.value, max_value.value
    
    def _get_maximum_adc_value(self) -> int:
        """
        Gets the ADC limits for specified devices.

        Currently tested on: 6000a.

        Returns:
                int: Maximum ADC value.
        """
        max_value = ctypes.c_int16()
        self._call_attr_function(
            'MaximumValue',
            self.handle,
            ctypes.byref(max_value)
        )
        return max_value.value
    
    def get_time_axis(self, timebase:int, samples:int) -> list:
        """
        Return an array of time values based on the timebase and number
        of samples

        Args:
            timebase (int): PicoScope timebase 
            samples (int): Number of samples captured

        Returns:
            list: List of time values in nano-seconds
        """
        interval = self.get_timebase(timebase, samples)['Interval(ns)']
        return [round(x*interval, 4) for x in range(samples)]

    def get_trigger_info(
        self,
        first_segment_index: int = 0,
        segment_count: int = 1,
    ) -> list[dict]:
        """Retrieve trigger timing information for one or more segments.

        Args:
            first_segment_index: Index of the first memory segment to query.
            segment_count: Number of consecutive segments starting at
                ``first_segment_index``.

        Returns:
            List of dictionaries for each trigger event

        Raises:
            PicoSDKException: If the function call fails or preconditions are
                not met.
        """

        info_array = (PICO_TRIGGER_INFO * segment_count)()

        self._call_attr_function(
            "GetTriggerInfo",
            self.handle,
            ctypes.byref(info_array[0]),
            ctypes.c_uint64(first_segment_index),
            ctypes.c_uint64(segment_count),
        )

        # Convert struct to dictionary
        return [_struct_to_dict(info, format=True) for info in info_array]
    
    def get_trigger_time_offset(self, time_unit: TIME_UNIT, segment_index: int = 0) -> int:
        """
        Get the trigger time offset for jitter correction in waveforms.

        The driver interpolates between adjacent samples to estimate when the
        trigger actually occurred.  This means the value returned can have a
        very fine granularity—down to femtoseconds—even though the effective
        resolution is usually limited to roughly one-tenth of the sampling
        interval in real-world use.

        Args:
            time_unit (TIME_UNIT): Desired unit for the returned offset.
            segment_index (int, optional): The memory segment to query. Default
                is 0.

        Returns:
            int: Trigger time offset converted to ``time_unit``.

        Raises:
            PicoSDKException: If the function call fails or preconditions are
                not met.
        """
        time = ctypes.c_int64()
        returned_unit = ctypes.c_int32()

        self._call_attr_function(
            'GetTriggerTimeOffset',
            self.handle,
            ctypes.byref(time),
            ctypes.byref(returned_unit),
            ctypes.c_uint64(segment_index)
        )

        # Convert the returned time to the requested ``time_unit``
        pico_unit = PICO_TIME_UNIT(returned_unit.value)
        time_s = time.value / TIME_UNIT[pico_unit.name]
        return int(time_s * TIME_UNIT[time_unit.name])

    def get_values_trigger_time_offset_bulk(
        self,
        from_segment_index: int,
        to_segment_index: int,
    ) -> list[tuple[int, PICO_TIME_UNIT]]:
        """Retrieve trigger time offsets for a range of segments.

        This method returns the trigger time offset and associated 
        time unit for each requested segment.

        Args:
            from_segment_index: Index of the first memory segment to query.
            to_segment_index: Index of the last memory segment. If this value
                is less than ``from_segment_index`` the driver wraps around.

        Returns:
            list[tuple[int, PICO_TIME_UNIT]]: ``[(offset, unit), ...]`` for each
            segment beginning with ``from_segment_index``.
        """

        count = to_segment_index - from_segment_index + 1
        times = (ctypes.c_int64 * count)()
        units = (ctypes.c_int32 * count)()

        self._call_attr_function(
            "GetValuesTriggerTimeOffsetBulk",
            self.handle,
            ctypes.byref(times),
            ctypes.byref(units),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
        )

        results = []
        for i in range(count):
            results.append((times[i], PICO_TIME_UNIT(units[i])))
        return results

    def set_no_of_captures(self, n_captures: int) -> None:
        """Configure the number of captures for rapid block mode."""

        self._call_attr_function(
            "SetNoOfCaptures",
            self.handle,
            ctypes.c_uint64(n_captures),
        )

    def get_no_of_captures(self) -> int:
        """Return the number of captures configured for rapid block."""

        n_captures = ctypes.c_uint64()
        self._call_attr_function(
            "GetNoOfCaptures",
            self.handle,
            ctypes.byref(n_captures),
        )
        return n_captures.value

    def get_values_bulk(
        self,
        start_index: int,
        no_of_samples: int,
        from_segment_index: int,
        to_segment_index: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
    ) -> int:
        """Retrieve data from multiple memory segments.
        
        Returns:
            tuple[int, int] number of samples and overflow value"""

        self.is_ready()
        no_samples = ctypes.c_uint64(no_of_samples)
        overflow = ctypes.c_int16()
        self._call_attr_function(
            "GetValuesBulk",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.byref(no_samples),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            ctypes.byref(overflow),
        )
        self.over_range = overflow.value
        self.is_over_range()
        return no_samples.value, overflow.value

    def get_values_bulk_async(
        self,
        start_index: int,
        no_of_samples: int,
        from_segment_index: int,
        to_segment_index: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
        lp_data_ready,
        p_parameter,
    ) -> None:
        """Begin asynchronous retrieval of values from multiple segments."""

        self._call_attr_function(
            "GetValuesBulkAsync",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.c_uint64(no_of_samples),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            lp_data_ready,
            p_parameter,
        )

    def get_values_overlapped(
        self,
        start_index: int,
        no_of_samples: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
        from_segment_index: int,
        to_segment_index: int,
        overflow: ctypes.c_int16,
    ) -> int:
        """Retrieve overlapped data from multiple segments."""

        self.is_ready()
        c_samples = ctypes.c_uint64(no_of_samples)
        self._call_attr_function(
            "GetValuesOverlapped",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.byref(c_samples),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.byref(overflow),
        )
        self.over_range = overflow.value
        self.is_over_range()
        return c_samples.value

    def stop_using_get_values_overlapped(self) -> None:
        """Terminate overlapped capture mode."""

        self._call_attr_function(
            "StopUsingGetValuesOverlapped",
            self.handle,
        )


    
    # Data conversion ADC/mV & ctypes/int 
    def mv_to_adc(self, mv: float, channel_range: int, channel: typing.Optional[CHANNEL] = None) -> int:
        """
        Converts a millivolt (mV) value to an ADC value based on the device's
        maximum ADC range.

        Args:
                mv (float): Voltage in millivolts to be converted.
                channel_range (int): Range of channel in millivolts i.e. 500 mV.
                channel (CHANNEL, optional): Channel associated with ``mv``. The
                        probe scaling for the channel will be applied if provided.

        Returns:
                int: ADC value corresponding to the input millivolt value.
        """
        scale = self.probe_scale.get(channel, 1)
        channel_range_mv = RANGE_LIST[channel_range]
        return int(((mv / scale) / channel_range_mv) * self.max_adc_value)

    def adc_to_mv(self, adc: int, channel_range: int, channel: typing.Optional[CHANNEL] = None):
        """Converts ADC value to mV using the stored probe scaling."""
        scale = self.probe_scale.get(channel, 1)
        channel_range_mv = float(RANGE_LIST[channel_range])
        return ((float(adc) / float(self.max_adc_value)) * channel_range_mv) * scale
    
    def buffer_adc_to_mv(self, buffer: list, channel: str) -> list:
        """Converts an ADC buffer list to mV list"""
        return [self.adc_to_mv(sample, self.range[channel], channel) for sample in buffer]
    
    def channels_buffer_adc_to_mv(self, channels_buffer: dict) -> dict:
        "Converts dict of multiple channels adc values to millivolts (mV)"
        for channel in channels_buffer:
            # Get channel data (mv range and probe scaling)
            channel_range_mv = RANGE_LIST[self.range[channel]]
            channel_scale = self.probe_scale[channel]
            # Extract data
            data = channels_buffer[channel]

            # If data is rapid block array
            if type(data[0]) == np.ndarray:
                for n, array in enumerate(data):
                    channels_buffer[channel][n] = ((array / self.max_adc_value) * channel_range_mv) * channel_scale
            # Else anything else is converted normally
            else:
                channels_buffer[channel] = ((data / self.max_adc_value) * channel_range_mv) * channel_scale
        return channels_buffer
    
    def buffer_ctypes_to_list(self, ctypes_list):
        "Converts a ctype dataset into a python list of samples"
        return [sample for sample in ctypes_list]
    
    def channels_buffer_ctype_to_list(self, channels_buffer):
        "Takes a ctypes channel dictionary buffer and converts into a integer array."
        for channel in channels_buffer:
            channels_buffer[channel] = self.buffer_ctypes_to_list(channels_buffer[channel])
        return channels_buffer

    # Set methods for PicoScope configuration    
    def _change_power_source(self, state: POWER_SOURCE) -> 0:
        """
        Change the power source of a device to/from USB only or DC + USB.

        Args:
                state (POWER_SOURCE): Power source variable (i.e. POWER_SOURCE.SUPPLY_NOT_CONNECTED).
        """
        self._call_attr_function(
            'ChangePowerSource',
            self.handle,
            state
        )

    def _set_channel_on(self, channel, range, coupling=COUPLING.DC, offset=0.0, bandwidth=BANDWIDTH_CH.FULL):
        """Sets a channel to ON at a specified range (6000E)"""
        self.range[channel] = range
        attr_function = getattr(self.dll, self._unit_prefix_n + 'SetChannelOn')
        status = attr_function(
            self.handle,
            channel,
            coupling,
            range,
            ctypes.c_double(offset),
            bandwidth
        )
        return self._error_handler(status)
    
    def _set_channel_off(self, channel):
        """Sets a channel to OFF (6000E)"""
        attr_function = getattr(self.dll, self._unit_prefix_n + 'SetChannelOff')
        status = attr_function(
            self.handle, 
            channel
        )
        return self._error_handler(status)
    
    def set_all_channels_off(self):
        """Turns all channels off, based on unit number of channels"""
        channels = self.get_unit_info(UNIT_INFO.PICO_VARIANT_INFO)[1]
        for channel in range(int(channels)):
            self.set_channel(channel, enabled=False)
    
    
    def set_simple_trigger(self, channel, threshold_mv, enable=True, direction=TRIGGER_DIR.RISING, delay=0, auto_trigger=0):
        """Configure a simple edge trigger.

        Args:
            channel (int): The input channel to apply the trigger to.
            threshold_mv (float): Trigger threshold level in millivolts.
            enable (bool, optional): Enables or disables the trigger.
            direction (TRIGGER_DIR, optional): Trigger direction (e.g., ``TRIGGER_DIR.RISING``).
            delay (int, optional): Delay in samples after the trigger condition is met before starting capture.
            auto_trigger (int, optional): Timeout in **microseconds** after which data capture proceeds even if no
                trigger occurs. If 0, the PicoScope will wait indefintely.
        """
        if channel in self.range:
            threshold_adc = self.mv_to_adc(threshold_mv, self.range[channel], channel)
        else:
            threshold_adc = int(threshold_mv)
        self._call_attr_function(
            'SetSimpleTrigger',
            self.handle,
            enable,
            channel,
            threshold_adc,
            direction,
            delay,
            auto_trigger
        )

    def set_trigger_channel_conditions(
        self,
        source: int,
        state: int,
        action: int = ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> None:
        """Configure a trigger condition.

        Args:
            source (int): Input source as a :class:`CHANNEL` value.
            state (int): Desired state from :class:`PICO_TRIGGER_STATE`.
            action (int, optional): How to apply this condition relative to any
                previous configuration. Defaults to ``ACTION.CLEAR_ALL | ACTION.ADD``.
        """

        cond = PICO_CONDITION(source, state)

        self._call_attr_function(
            "SetTriggerChannelConditions",
            self.handle,
            ctypes.byref(cond),
            ctypes.c_int16(1),
            action,
        )

    def set_trigger_channel_properties(
        self,
        threshold_upper: int,
        hysteresis_upper: int,
        threshold_lower: int,
        hysteresis_lower: int,
        channel: int,
        aux_output_enable: int = 0,
        auto_trigger_us: int = 0,
    ) -> None:
        """Configure trigger thresholds for ``channel``. All
        threshold and hysteresis values are specified in ADC counts.

        Args:
            threshold_upper (int): Upper trigger level.
            hysteresis_upper (int): Hysteresis for ``threshold_upper``.
            threshold_lower (int): Lower trigger level.
            hysteresis_lower (int): Hysteresis for ``threshold_lower``.
            channel (int): Target channel as a :class:`CHANNEL` value.
            aux_output_enable (int, optional): Auxiliary output flag.
            auto_trigger_us (int, optional): Auto-trigger timeout in
                microseconds. ``0`` waits indefinitely.
        """

        prop = PICO_TRIGGER_CHANNEL_PROPERTIES(
            threshold_upper,
            hysteresis_upper,
            threshold_lower,
            hysteresis_lower,
            channel,
        )

        self._call_attr_function(
            "SetTriggerChannelProperties",
            self.handle,
            ctypes.byref(prop),
            ctypes.c_int16(1),
            ctypes.c_int16(aux_output_enable),
            ctypes.c_uint32(auto_trigger_us),
        )

    def set_trigger_channel_directions(
        self,
        channel: int,
        direction: int,
        threshold_mode: int,
    ) -> None:
        """Specify the trigger direction for ``channel``.

        Args:
            channel (int): Channel to configure.
            direction (int): Direction value from
                :class:`PICO_THRESHOLD_DIRECTION`.
            threshold_mode (int): Threshold mode from
                :class:`PICO_THRESHOLD_MODE`.
        """

        dir_struct = PICO_DIRECTION(channel, direction, threshold_mode)

        self._call_attr_function(
            "SetTriggerChannelDirections",
            self.handle,
            ctypes.byref(dir_struct),
            ctypes.c_int16(1),
        )

    def set_advanced_trigger(
        self,
        channel: int,
        state: int,
        direction: int,
        threshold_mode: int,
        threshold_upper_mv: float,
        threshold_lower_mv: float,
        hysteresis_upper_mv: float = 0.0,
        hysteresis_lower_mv: float = 0.0,
        aux_output_enable: int = 0,
        auto_trigger_ms: int = 0,
        action: int = ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> None:
        """Configure an advanced trigger in a single call.

        This helper sets up the trigger condition, direction and properties
        required for non-simple triggers.

        Args:
            channel: Channel to monitor for the trigger condition.
            state: Trigger state used with ``set_trigger_channel_conditions``.
            direction: Trigger direction from
                :class:`PICO_THRESHOLD_DIRECTION`.
            threshold_mode: Threshold mode from :class:`PICO_THRESHOLD_MODE`.
            threshold_upper_mv: Upper trigger threshold in millivolts.
            threshold_lower_mv: Lower trigger threshold in millivolts.
            hysteresis_upper_mv: Optional hysteresis for ``threshold_upper_mv``
                in millivolts.
            hysteresis_lower_mv: Optional hysteresis for ``threshold_lower_mv``
                in millivolts.
            aux_output_enable: Optional auxiliary output flag.
            auto_trigger_ms: Auto-trigger timeout in milliseconds. ``0`` waits
                indefinitely.
            action: Action flag for ``set_trigger_channel_conditions``.
        """

        if channel in self.range:
            upper_adc = self.mv_to_adc(threshold_upper_mv, self.range[channel], channel)
            lower_adc = self.mv_to_adc(threshold_lower_mv, self.range[channel], channel)
            hyst_upper_adc = self.mv_to_adc(hysteresis_upper_mv, self.range[channel], channel)
            hyst_lower_adc = self.mv_to_adc(hysteresis_lower_mv, self.range[channel], channel)
        else:
            upper_adc = int(threshold_upper_mv)
            lower_adc = int(threshold_lower_mv)
            hyst_upper_adc = int(hysteresis_upper_mv)
            hyst_lower_adc = int(hysteresis_lower_mv)

        self.set_trigger_channel_conditions(channel, state, action)
        self.set_trigger_channel_directions(channel, direction, threshold_mode)
        self.set_trigger_channel_properties(
            upper_adc,
            hyst_upper_adc,
            lower_adc,
            hyst_lower_adc,
            channel,
            aux_output_enable,
            auto_trigger_ms * 1000,
        )
    
    def set_data_buffer_for_enabled_channels():
        raise NotImplementedError("Method not yet available for this oscilloscope")
    
    
    def _set_data_buffer_ps6000a(
        self,
        channel,
        samples,
        segment=0,
        datatype=DATA_TYPE.INT16_T,
        ratio_mode=RATIO_MODE.RAW,
        action=ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> np.ndarray | None:
        """
        Allocates and assigns a data buffer for a specified channel on the 6000A series.

        Args:
            channel (int): The channel to associate the buffer with (e.g., CHANNEL.A).
            samples (int): Number of samples to allocate in the buffer.
            segment (int, optional): Memory segment to use. 
            datatype (DATA_TYPE, optional): C data type for the buffer (e.g., INT16_T). 
            ratio_mode (RATIO_MODE, optional): Downsampling mode. 
            action (ACTION, optional): Action to apply to the data buffer (e.g., CLEAR_ALL | ADD).

        Returns:
            np.array | None: The allocated buffer or ``None`` when clearing existing buffers.

        Raises:
            PicoSDKException: If an unsupported data type is provided.
        """
        if samples == 0:
            buffer = None
            buf_ptr = None
        else:
            # Map to NumPy dtype
            dtype_map = {
                DATA_TYPE.INT8_T: np.int8,
                DATA_TYPE.INT16_T: np.int16,
                DATA_TYPE.INT32_T: np.int32,
                DATA_TYPE.INT64_T: np.int64,
                DATA_TYPE.UINT32_T: np.uint32,
            }

            np_dtype = dtype_map.get(datatype)
            if np_dtype is None:
                raise PicoSDKException("Invalid datatype selected for buffer")

            buffer = np.zeros(samples, dtype=np_dtype)
            buf_ptr = npc.as_ctypes(buffer)

        self._call_attr_function(
            "SetDataBuffer",
            self.handle,
            channel,
            buf_ptr,
            samples,
            datatype,
            segment,
            ratio_mode,
            action,
        )
        return buffer

    def _set_data_buffers_ps6000a(
        self,
        channel,
        samples,
        segment=0,
        datatype=DATA_TYPE.INT16_T,
        ratio_mode=RATIO_MODE.AGGREGATE,
        action=ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Allocate and assign max and min NumPy-backed data buffers for 6000A series.

        Args:
            channel (int): The channel to associate the buffers with.
            samples (int): Number of samples to allocate.
            segment (int, optional): Memory segment to use.
            datatype (DATA_TYPE, optional): C data type for the buffer (e.g., INT16_T).
            ratio_mode (RATIO_MODE, optional): Downsampling mode.
            action (ACTION, optional): Action to apply to the data buffer.

        Returns:
            tuple[np.ndarray, np.ndarray]: Tuple of (buffer_min, buffer_max) NumPy arrays.

        Raises:
            PicoSDKException: If an unsupported data type is provided.
        """
        # Map to NumPy dtype
        dtype_map = {
            DATA_TYPE.INT8_T: np.int8,
            DATA_TYPE.INT16_T: np.int16,
            DATA_TYPE.INT32_T: np.int32,
            DATA_TYPE.INT64_T: np.int64,
            DATA_TYPE.UINT32_T: np.uint32,
        }

        np_dtype = dtype_map.get(datatype)
        if np_dtype is None:
            raise PicoSDKException("Invalid datatype selected for buffer")

        buffer_max = np.zeros(samples, dtype=np_dtype)
        buffer_min = np.zeros(samples, dtype=np_dtype)

        buf_max_ptr = npc.as_ctypes(buffer_max)
        buf_min_ptr = npc.as_ctypes(buffer_min)

        self._call_attr_function(
            "SetDataBuffers",
            self.handle,
            channel,
            buf_max_ptr,
            buf_min_ptr,
            samples,
            datatype,
            segment,
            ratio_mode,
            action,
        )

        return buffer_min, buffer_max

    
    # Run functions
    def run_block_capture(self, timebase, samples, pre_trig_percent=50, segment=0) -> int:
        """
        Runs a block capture using the specified timebase and number of samples.

        This sets up the PicoScope to begin collecting a block of data, divided into
        pre-trigger and post-trigger samples. It uses the PicoSDK `RunBlock` function.

        Args:
                timebase (int): Timebase value determining sample interval (refer to PicoSDK guide).
                samples (int): Total number of samples to capture.
                pre_trig_percent (int, optional): Percentage of samples to capture before the trigger. 
                segment (int, optional): Memory segment index to use.

        Returns:
                int: Estimated time (in milliseconds) the device will be busy capturing data.
        """

        pre_samples = int((samples * pre_trig_percent) / 100)
        post_samples = int(samples - pre_samples)
        time_indisposed_ms = ctypes.c_int32()
        self._call_attr_function(
            'RunBlock',
            self.handle,
            pre_samples,
            post_samples,
            timebase,
            ctypes.byref(time_indisposed_ms),
            segment,
            None,
            None
        )
        return time_indisposed_ms.value
    
    def run_streaming(
        self,
        sample_interval: float,
        time_units: PICO_TIME_UNIT,
        max_pre_trigger_samples: int,
        max_post_trigger_samples: int,
        auto_stop: int,
        ratio: int,
        ratio_mode: RATIO_MODE,
    ) -> float:
        """Begin a streaming capture.
        This wraps the ``RunStreaming`` driver call and configures the
        acquisition according to the provided arguments.
        Args:
            sample_interval: Requested interval between samples.
            time_units: Unit for ``sample_interval``.
            max_pre_trigger_samples: Number of pre-trigger samples to collect.
            max_post_trigger_samples: Number of post-trigger samples to collect.
            auto_stop: Whether the driver should stop when the buffer is full.
            ratio: Down sampling ratio.
            ratio_mode: Down sampling mode.
        Returns:
            float: The actual sample interval configured by the driver.
        """

        c_sample_interval = ctypes.c_double(sample_interval)
        self._call_attr_function(
            "RunStreaming",
            self.handle,
            ctypes.byref(c_sample_interval),
            time_units,
            max_pre_trigger_samples,
            max_post_trigger_samples,
            auto_stop,
            ratio,
            ratio_mode,
        )
        return c_sample_interval.value
    
    def get_enumerated_units(self) -> tuple[int, str, int]:
        """
        Returns count, serials and serial string length of a specific PicoScope unit.

        Returns:
            Number of devices of this type
            Comma separated string of all serials
            Length of string
        """
        string_buffer_length = 256
        count = ctypes.c_int16()
        serials = ctypes.create_string_buffer(string_buffer_length)
        serial_length = ctypes.c_int16(string_buffer_length)
        self._call_attr_function(
            'EnumerateUnits',
            ctypes.byref(count),
            ctypes.byref(serials),
            ctypes.byref(serial_length)
        )
        return count.value, serials.value.decode(), serial_length.value
    
    def get_values(self, samples, start_index=0, segment=0, ratio=0, ratio_mode=RATIO_MODE.RAW) -> int:
        """
        Retrieves a block of captured samples from the device once it's ready.
        If a channel goes over-range a warning will appear.

        This function should be called after confirming the device is ready using `is_ready()`.
        It invokes the underlying PicoSDK `GetValues` function to read the data into memory.

        Args:
                samples (int): Number of samples to retrieve.
                start_index (int, optional): Starting index in the buffer.
                segment (int, optional): Memory segment index to retrieve data from.
                ratio (int, optional): Downsampling ratio.
                ratio_mode (RATIO_MODE, optional): Ratio mode for downsampling. 

        Returns:
                int: Actual number of samples retrieved.
        """

        self.is_ready()
        total_samples = ctypes.c_uint32(samples)
        over_range = ctypes.c_int16()
        self._call_attr_function(
            'GetValues',
            self.handle, 
            start_index,
            ctypes.byref(total_samples),
            ratio,
            ratio_mode,
            segment,
            ctypes.byref(over_range)
        )
        self.over_range = over_range.value
        self.is_over_range()
        return total_samples.value

    
    def is_over_range(self) -> list:
        """
        Logs and prints a warning if any channel has been over range.

        Returns:
            list: List of channels that have been over range
        """

        over_range_channels = [CHANNEL_NAMES[i] for i in range(8) if self.over_range & (1 << i)]
    
        if over_range_channels:
            warnings.warn(
                f"Overrange detected on channels: {', '.join(over_range_channels)}.",
                OverrangeWarning
            )
        return over_range_channels
        
    
    def run_simple_block_capture(self) -> dict:
        raise NotImplementedError("This method is not yet implemented in this PicoScope")
    
    # Siggen Functions
    def _siggen_apply(self, enabled=1, sweep_enabled=0, trigger_enabled=0, 
                     auto_clock_optimise_enabled=0, override_auto_clock_prescale=0) -> dict:
        """
        Sets the signal generator running using parameters previously configured.

        Args:
                enabled (int, optional): SigGen Enabled, 
                sweep_enabled (int, optional): Sweep Enabled,
                trigger_enabled (int, optional): SigGen trigger enabled,
                auto_clock_optimise_enabled (int, optional): Auto Clock Optimisation,
                override_auto_clock_prescale (int, optional): Override Clock Prescale,

        Returns:
                dict: Returns dictionary of the actual achieved values.
        """
        c_frequency = ctypes.c_double()
        c_stop_freq = ctypes.c_double()
        c_freq_incr = ctypes.c_double()
        c_dwell_time = ctypes.c_double()
        self._call_attr_function(
            'SigGenApply',
            self.handle,
            enabled,
            sweep_enabled,
            trigger_enabled,
            auto_clock_optimise_enabled,
            override_auto_clock_prescale,
            ctypes.byref(c_frequency),
            ctypes.byref(c_stop_freq),
            ctypes.byref(c_freq_incr),
            ctypes.byref(c_dwell_time)
        )
        return {'Freq': c_frequency.value,
                'StopFreq': c_stop_freq.value,
                'FreqInc': c_freq_incr.value,
                'dwelltime': c_dwell_time.value}
    
    def _siggen_set_frequency(self, frequency:float) -> None:
        """
        Set frequency of SigGen in Hz.

        Args:
                frequency (int): Frequency in Hz.
        """   
        self._call_attr_function(
            'SigGenFrequency',
            self.handle,
            ctypes.c_double(frequency)
        )

    def _siggen_set_duty_cycle(self, duty:float) -> None:
        """
        Set duty cycle of SigGen in percentage

        Args:
                duty cycle (int): Duty cycle in %.
        """   
        self._call_attr_function(
            'SigGenWaveformDutyCycle',
            self.handle,
            ctypes.c_double(duty)
        )
    
    def _siggen_set_range(self, pk2pk:float, offset:float=0.0):
        """
        Set mV range of SigGen (6000A).

        Args:
                pk2pk (int): Peak to peak of signal in volts (V).
                offset (int, optional): Offset of signal in volts (V).
        """      
        self._call_attr_function(
            'SigGenRange',
            self.handle,
            ctypes.c_double(pk2pk),
            ctypes.c_double(offset)
        )
    
    def _siggen_set_waveform(self, wave_type: WAVEFORM):
        """
        Set waveform type for SigGen (6000A).

        Args:
                wave_type (WAVEFORM): Waveform type i.e. WAVEFORM.SINE.
        """
        self._call_attr_function(
            'SigGenWaveform',
            self.handle,
            wave_type,
            None,
            None
        )

    def set_siggen(self, *args):
        raise NotImplementedError("Method not yet available for this oscilloscope")


__all__ = ['PicoSDKNotFoundException', 'PicoSDKException', 'OverrangeWarning', 'PowerSupplyWarning', 'PicoScopeBase']
