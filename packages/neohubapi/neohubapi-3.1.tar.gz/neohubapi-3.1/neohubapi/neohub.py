# SPDX-FileCopyrightText: 2020-2021 Andrius Štikonas <andrius@stikonas.eu>
# SPDX-FileCopyrightText: 2021 Dave O'Connor <daveoc@google.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""NeoHub main class."""

from abc import ABC, abstractmethod
import asyncio
import datetime
import itertools
import json
import logging
import socket
import ssl
from types import SimpleNamespace

import websockets
from websockets.exceptions import ConnectionClosed

from .enums import (
    ATTR_DEVICES,
    ATTR_LIVE,
    ATTR_PROFILES,
    ATTR_PROFILES_0,
    ATTR_SYSTEM,
    ATTR_TIMER_PROFILES,
    ATTR_TIMER_PROFILES_0,
    HCMode,
    ScheduleFormat,
    schedule_format_int_to_enum,
)
from .neostat import NeoStat


class Error(Exception):
    """Generic NeoHubApi error."""


class NeoHubUsageError(Error):
    """NeoHubApi usage error."""


class NeoHubConnectionError(Error):
    """NeoHubApi connection error."""


class NeoHub:
    """Class representing NeoHub."""

    _logger = logging.getLogger("neohub")

    def __init__(
        self,
        host="Neo-Hub",
        port=4242,
        request_timeout=60,
        request_attempts=1,
        token=None,
    ):
        """Initialize NeoHub."""
        self._host = host
        self._port = int(port)
        self._request_timeout = request_timeout
        self._request_attempts = request_attempts
        self._token = token
        # Sanity checks.
        if port not in (4242, 4243):
            raise NeoHubConnectionError(
                f"Invalid port number ({port}): use 4242 or 4243 instead"
            )
        if port == 4243 and token is None:
            raise NeoHubConnectionError(
                "You must provide a token for a connection on port 4243, or use a legacy connection on port 4242"
            )
        if port == 4242 and token is not None:
            raise NeoHubConnectionError(
                "You have provided a token, so you must use port=4243"
            )
        self._client: Client | None = None
        self._update_timestamps = {
            "TIMESTAMP_DEVICE_LISTS": None,
            "TIMESTAMP_ENGINEERS": None,
            "TIMESTAMP_PROFILE_0": None,
            "TIMESTAMP_PROFILE_COMFORT_LEVELS": None,
            "TIMESTAMP_PROFILE_TIMERS": None,
            "TIMESTAMP_PROFILE_TIMERS_0": None,
            "TIMESTAMP_RECIPES": None,
            "TIMESTAMP_SYSTEM": None,
        }
        self._eng_hub_data = None
        self._system_data = None
        self._profiles = None
        self._timer_profiles = None
        self._profiles_0 = None
        self._timer_profiles_0 = None
        self._profile_names = None
        self._device_sns = None
        self._mac_address = None
        self._firmware_version = None

    async def _send(self, message, expected_reply=None):
        """Send a message and handle retries."""
        last_exception = None
        for attempt in range(1, self._request_attempts + 1):
            try:
                if self._token is not None:
                    if self._client is None or not self._client.running:
                        self._client = WebSocketClient(
                            self._host,
                            self._port,
                            self._token,
                            self._logger,
                            self._request_timeout,
                        )
                        await self._client.start()
                    json_string = await self._client.send_message(message)
                    if not self._mac_address:
                        self._mac_address = self._client.mac_address
                else:
                    if self._client is None or not self._client.running:
                        self._client = LegacyClient(
                            self._host,
                            self._port,
                            self._logger,
                            self._request_timeout,
                        )
                        await self._client.start()
                    json_string = await self._client.send_message(message)

                self._logger.debug("Received message: %s", json_string)
                reply = json.loads(
                    json_string, object_hook=lambda d: SimpleNamespace(**d)
                )

                if expected_reply is None:
                    return reply
                if reply.__dict__ == expected_reply:
                    return True
                self._logger.error(
                    "[%s] Unexpected reply:%s for message: %s", attempt, reply, message
                )
            except (
                socket.gaierror,
                ConnectionRefusedError,
                websockets.InvalidHandshake,
            ) as e:
                last_exception = NeoHubConnectionError(e)
                self._logger.exception(
                    "[%s] Could not connect to NeoHub at %s", attempt, self._host
                )
            except TimeoutError as e:
                last_exception = e
                self._logger.exception(
                    "[%s] Timed out while sending a message to %s", attempt, self._host
                )
                if self._client:
                    await self._client.disconnect()
            except websockets.ConnectionClosedError:
                last_exception = NeoHubConnectionError("WebSocket connection closed")
                self._logger.exception(
                    "[%s] Connection forcibly closed - maybe a bad token?", attempt
                )
                if self._client:
                    await self._client.disconnect()
            except json.decoder.JSONDecodeError as e:
                last_exception = e
                self._logger.exception("[%s] Could not decode JSON", attempt)
                if self._client:
                    await self._client.disconnect()
            except ConnectionError as e:
                last_exception = NeoHubConnectionError(e)
                self._logger.exception("[%s] Connection error", attempt)
                if self._client:
                    await self._client.disconnect()
            # Wait for 1/2 of the timeout value before retrying.
            if self._request_attempts > 1 and attempt < self._request_attempts:
                await asyncio.sleep(self._request_timeout / 2)

        if expected_reply is None and last_exception is not None:
            raise last_exception
        return False

    def _devices_to_device_ids(self, devices: list[NeoStat]):
        """Return the list of device ids."""
        try:
            return [x.device_id for x in devices]
        except (TypeError, AttributeError) as err:
            raise NeoHubUsageError("devices must be a list of NeoStat objects") from err

    def _devices_to_names(self, devices: list[NeoStat]):
        """Return the list of device names."""
        try:
            return [x.name for x in devices]
        except (TypeError, AttributeError) as err:
            raise NeoHubUsageError("devices must be a list of NeoStat objects") from err

    async def firmware(self):
        """NeoHub firmware version."""

        if self._firmware_version is None:
            message = {"FIRMWARE": 0}
            result = await self._send(message)
            self._firmware_version = int(getattr(result, "firmware version"))
        return self._firmware_version

    async def get_system(self):
        """Get system wide variables."""
        message = {"GET_SYSTEM": 0}

        data = await self._send(message)
        data.FORMAT = schedule_format_int_to_enum(data.FORMAT)
        data.ALT_TIMER_FORMAT = schedule_format_int_to_enum(data.ALT_TIMER_FORMAT)
        return data

    async def target_temperature_step(self):
        """Return Neohub's target temperature step."""

        if await self.firmware() >= 2135:
            return 0.5
        return 1

    @property
    def mac_address(self) -> str | None:
        """Return the NeoHub's MAC address. Only when using Websocket API."""
        return self._mac_address

    async def reset(self):
        """Reboot neohub.

        Returns True if Restart is initiated
        """

        message = {"RESET": 0}
        reply = {"Restarting": 1}

        firmware_version = await self.firmware()
        if firmware_version >= 2027:
            return await self._send(message, reply)
        return False

    async def set_channel(self, channel: int):
        """Set ZigBee channel.

        Only channels 11, 14, 15, 19, 20, 24, 25 are allowed.
        """

        try:
            message = {"SET_CHANNEL": int(channel)}
        except ValueError as err:
            raise NeoHubUsageError("channel must be a number") from err

        reply = {"result": "Trying to change channel"}

        return await self._send(message, reply)

    async def set_temp_format(self, temp_format: str):
        """Set temperature format to C or F."""

        message = {"SET_TEMP_FORMAT": temp_format}
        reply = {"result": f"Temperature format set to {temp_format}"}

        return await self._send(message, reply)

    async def set_hc_mode(self, hc_mode: HCMode, devices: list[NeoStat]):
        """Set hc_mode to AUTO or..."""
        names = self._devices_to_names(devices)
        message = {"SET_HC_MODE": [hc_mode.value, names]}
        reply = {"result": "HC_MODE was set"}

        return await self._send(message, reply)

    async def set_format(self, sched_format: ScheduleFormat):
        """Set schedule format.

        Format is specified using ScheduleFormat enum:
        """
        if not isinstance(sched_format, ScheduleFormat):
            raise NeoHubUsageError("sched_format must be a ScheduleFormat")

        message = {"SET_FORMAT": sched_format.value}
        reply = {"result": "Format was set"}

        return await self._send(message, reply)

    async def set_away(self, state: bool):
        """Enable away mode for all devices.

        Puts thermostats into frost mode and timeclocks are set to off.
        Instead of this function it is recommended to use frost on/off commands

        List of affected devices can be restricted using GLOBAL_DEV_LIST command
        """

        message = {"AWAY_ON" if state else "AWAY_OFF": 0}
        reply = {"result": "away on" if state else "away off"}

        return await self._send(message, reply)

    async def set_holiday(self, start: datetime.datetime, end: datetime.datetime):
        """Set holiday mode.

        start: beginning of holiday
        end: end of holiday
        """
        for datetime_arg in (start, end):
            if not isinstance(datetime_arg, datetime.datetime):
                raise NeoHubUsageError(
                    "start and end must be datetime.datetime objects"
                )

        message = {
            "HOLIDAY": [start.strftime("%H%M%S%d%m%Y"), end.strftime("%H%M%S%d%m%Y")]
        }

        return await self._send(message)

    async def get_holiday(self):
        """Get list of holidays.

        start end end times are converted to datetimes
        """
        message = {"GET_HOLIDAY": 0}

        result = await self._send(message)
        result.start = (
            datetime.datetime.strptime(result.start.strip(), "%a %b %d %H:%M:%S %Y")
            if result.start
            else None
        )
        result.end = (
            datetime.datetime.strptime(result.end.strip(), "%a %b %d %H:%M:%S %Y")
            if result.end
            else None
        )
        return result

    async def cancel_holiday(self):
        """Cancel holidays and returns to normal schedule."""

        message = {"CANCEL_HOLIDAY": 0}
        reply = {"result": "holiday cancelled"}

        return await self._send(message, reply)

    async def get_devices(self):
        """Return list of devices.

        {"result": ["device1"]}
        """

        message = {"GET_DEVICES": 0}

        return await self._send(message)

    async def get_device_list(self, zone: str):
        """Return list of devices associated with zone."""

        message = {"GET_DEVICE_LIST": zone}

        result = await self._send(message)
        if "error" in result:
            return False
        return result[zone]

    async def devices_sn(self):
        """Return serial numbers of attached devices.

        {'name': [id, 'serial', 1], ...}
        """

        message = {"DEVICES_SN": 0}

        return await self._send(message)

    async def set_ntp(self, state: bool):
        """Enable NTP client on Neohub."""

        message = {"NTP_ON" if state else "NTP_OFF": 0}
        reply = {"result": "ntp client started" if state else "ntp client stopped"}

        return await self._send(message, reply)

    async def set_date(self, date: datetime.datetime = datetime.datetime.today()):
        """Set current date.

        By default, set to current date. Can be optionally passed datetime.datetime object
        """

        message = {"SET_DATE": [date.year, date.month, date.day]}
        reply = {"result": "Date is set"}

        return await self._send(message, reply)

    async def set_time(self, time: datetime.datetime = datetime.datetime.now()):
        """Set current time.

        By default, set to current time. Can be optionally passed datetime.datetime object
        """
        message = {"SET_TIME": [time.hour, time.minute]}
        reply = {"result": "time set"}

        return await self._send(message, reply)

    async def set_datetime(
        self, date_time: datetime.datetime = datetime.datetime.now()
    ):
        """Set both date and time."""

        result = await self.set_date(date_time)
        if result:
            result = await self.set_time(date_time)
        return result

    async def manual_dst(self, state: bool):
        """Manually enables/disables daylight saving time."""

        message = {"MANUAL_DST": int(state)}
        reply = {"result": "Updated time"}

        return await self._send(message, reply)

    async def set_dst(self, state: bool, region: str | None = None):
        """Enables/disables automatic DST handling.

        By default it uses UK dates for turning DST on/off.
        Available options for region are UK, EU, NZ.
        """

        message = {"DST_ON" if state else "DST_OFF": 0 if region is None else region}
        reply = {"result": "dst on" if state else "dst off"}

        valid_timezones = ["UK", "EU", "NZ"]
        if state and region not in valid_timezones:
            raise NeoHubUsageError(f"region must be in {valid_timezones}")

        return await self._send(message, reply)

    async def set_timezone(self, tz: float):
        """Set time zone."""

        message = {"TIME_ZONE": tz}
        reply = {"result": "timezone set"}

        return await self._send(message, reply)

    async def identify(self):
        """Flashes red LED light."""

        message = {"IDENTIFY": 0}
        reply = {"result": "flashing led"}

        return await self._send(message, reply)

    async def get_live_data(self):
        """Return live data from hub and all devices."""

        message = {"GET_LIVE_DATA": 0}
        return await self._send(message)

    async def permit_join(self, name, timeout_s: int = 120):
        """Permit new thermostat to join network.

        name: new zone will be added with this name
        timeout: duration of discovery mode in seconds

        To actually join network you need to select 01
        from the thermostat's setup menu.
        """

        message = {"PERMIT_JOIN": [timeout_s, name]}
        reply = {"result": "network allows joining"}

        return await self._send(message, reply)

    async def permit_repeater_join(self, timeout_s: int = 120):
        """Permit new repeaters to join network."""

        message = {"PERMIT_JOIN": ["repeater", timeout_s]}

        return await self._send(message)

    async def remove_repeater(self, repeater_name: str):
        """Handle repeater removal."""
        message = {"REMOVE_REPEATER": repeater_name}

        return await self._send(message)

    async def set_lock(self, pin: int, devices: list[NeoStat]):
        """PIN locks thermostats.

        PIN is a four digit number
        """

        try:
            if pin < 0 or pin > 9999:
                return False
        except TypeError as err:
            raise NeoHubUsageError("pin must be a number") from err

        pins = []
        for _ in range(4):
            pins.append(pin % 10)
            pin = pin // 10
        pins.reverse()

        names = self._devices_to_names(devices)
        message = {"LOCK": [pins, names]}
        reply = {"result": "locked"}

        return await self._send(message, reply)

    async def unlock(self, devices: list[NeoStat]):
        """Unlock PIN locked thermostats."""

        names = self._devices_to_names(devices)
        message = {"UNLOCK": names}
        reply = {"result": "unlocked"}

        return await self._send(message, reply)

    async def set_frost(self, state: bool, devices: list[NeoStat]):
        """Enable or disable Frost mode."""

        names = self._devices_to_names(devices)
        message = {"FROST_ON" if state else "FROST_OFF": names}
        reply = {"result": "frost on" if state else "frost off"}

        return await self._send(message, reply)

    async def set_frost_temp(self, temperature: float, devices: list[NeoStat]):
        """Set frost temperature."""

        names = self._devices_to_names(devices)
        message = {"SET_FROST": [temperature, names]}
        reply = {"result": "temperature was set"}

        result = await self._send(message, reply)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_cool_temp(self, temperature: int, devices: list[NeoStat]):
        """Set the thermostat's cooling temperature.

        i.e. the temperature that will
        trigger the thermostat if exceeded. Note that this is only supported on
        the HC (Heating/Cooling) thermostats.

        The temperature will be reset once next comfort level is reached
        """

        names = self._devices_to_names(devices)
        message = {"SET_COOL_TEMP": [temperature, names]}
        reply = {"result": "temperature was set"}

        return await self._send(message, reply)

    async def set_target_temperature(self, temperature: int, devices: list[NeoStat]):
        """Set the thermostat's temperature.

        The temperature will be reset once next comfort level is reached
        """

        names = self._devices_to_names(devices)
        message = {"SET_TEMP": [temperature, names]}
        reply = {"result": "temperature was set"}

        return await self._send(message, reply)

    async def set_diff(self, switching_differential: int, devices: list[NeoStat]):
        """Set the thermostat's switching differential.

        -1: Undocumented option. Seems to set differential to 204.
        0: 0.5 degrees
        1: 1 degree
        2: 2 degrees
        3: 3 degrees
        """

        names = self._devices_to_names(devices)
        message = {"SET_DIFF": [switching_differential, names]}
        reply = {"result": "switching differential was set"}

        result = await self._send(message, reply)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_output_delay(self, output_delay: int, devices: list[NeoStat]):
        """Set the thermostat's output delay."""

        names = self._devices_to_names(devices)
        message = {"SET_DELAY": [output_delay, names]}
        reply = {"result": "delay was set"}

        result = await self._send(message, reply)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_floor_limit(self, floor_limit: int, devices: list[NeoStat]):
        """Set the thermostat's floor limit temperature."""

        names = self._devices_to_names(devices)
        message = {"SET_FLOOR": [floor_limit, names]}
        # reply = {"result": "floor limit was set"}

        result = await self._send(message)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_user_limit(self, user_limit: int, devices: list[NeoStat]):
        """Set the thermostat's user limit temperature."""

        names = self._devices_to_names(devices)
        message = {"USER_LIMIT": [user_limit, names]}
        reply = {"result": "user limit set"}

        result = await self._send(message, reply)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_preheat(self, preheat_period: int, devices: list[NeoStat]):
        """Set the thermostat's preheat period."""

        names = self._devices_to_names(devices)
        message = {"SET_PREHEAT": [preheat_period, names]}
        reply = {"result": "max preheat was set"}

        result = await self._send(message, reply)
        self._update_timestamps["TIMESTAMP_ENGINEERS"] = 0
        return result

    async def set_fan_speed(self, fan_speed: str, devices: list[NeoStat]):
        """Set the thermostat's fan speed (NeoStat HC)."""

        names = self._devices_to_names(devices)
        message = {"SET_FAN_SPEED": [fan_speed, names]}
        # reply = {"result": "fan speed was set"}

        return await self._send(message)

    async def rate_of_change(self, devices: list[NeoStat]):
        """Return time in minutes required to change temperature by 1 degree."""

        names = self._devices_to_names(devices)
        message = {"VIEW_ROC": names}

        result = await self._send(message)
        return result.__dict__

    async def set_timer(self, state: bool, devices: list[NeoStat]):
        """Turn the output of timeclock on or off.

        This function works only with NeoPlugs and does not work on
        NeoStats that are in timeclock mode.
        """

        names = self._devices_to_names(devices)
        message = {"TIMER_ON" if state else "TIMER_OFF": names}
        reply = {"result": "timers on" if state else "timers off"}

        return await self._send(message, reply)

    async def set_manual(self, state: bool, devices: list[NeoStat]):
        """Control NeoPlug manual mode.

        Controls the timeclock built into the neoplug, can be enabled and disabled to allow for manual operation.
        This function works only with NeoPlugs and does not work on NeoStats that are in timeclock mode.
        """

        names = self._devices_to_names(devices)
        message = {"MANUAL_ON" if state else "MANUAL_OFF": names}
        reply = {"result": "manual on" if state else "manual off"}

        return await self._send(message, reply)

    async def set_hold(
        self, temperature: int, hours: int, minutes: int, devices: list[NeoStat]
    ):
        """Tells a thermostat to maintain the current temperature for a fixed time."""

        names = self._devices_to_names(devices)
        ids = self._devices_to_device_ids(devices)
        message = {
            "HOLD": [
                {
                    "temp": temperature,
                    "hours": hours,
                    "minutes": minutes,
                    "id": f"{ids}",
                },
                names,
            ]
        }
        reply = {"result": "temperature on hold"}

        return await self._send(message, reply)

    async def set_timer_hold(self, state: bool, minutes: int, devices: list[NeoStat]):
        """Turn the output of timeclock on or off for certain duration.

        This function works with NeoStats in timeclock mode
        """

        names = self._devices_to_names(devices)
        message = {"TIMER_HOLD_ON" if state else "TIMER_HOLD_OFF": [minutes, names]}
        reply = {"result": "timer hold on" if state else "timer hold off"}

        return await self._send(message, reply)

    async def set_profile_id(self, profile_id: int, devices: list[NeoStat]):
        """Set the profile id on a device."""

        names = self._devices_to_names(devices)

        message = {"RUN_PROFILE_ID": [profile_id, names]}
        reply = {"result": "profile was run"}

        return await self._send(message, reply)

    async def clear_profile_id(self, devices: list[NeoStat]):
        """Clear the profile id on a device."""

        names = self._devices_to_names(devices)

        message = {"CLEAR_CURRENT_PROFILE": names}
        reply = {"result": "Profile ID cleared"}

        return await self._send(message, reply)

    async def rename_profile(self, old_name: str, new_name: str):
        """Rename a profile."""

        message = {"PROFILE_TITLE": [old_name, new_name]}
        reply = {"result": "profile renamed"}

        return await self._send(message, reply)

    async def delete_profile(self, profile_name: str):
        """Delete a profile."""

        message = {"CLEAR_PROFILE": profile_name}
        reply = {"result": "profile removed"}

        return await self._send(message, reply)

    async def get_engineers(self):
        """Get engineers data."""
        message = {"GET_ENGINEERS": 0}

        return await self._send(message)

    async def get_profiles(self):
        """Get profiles."""

        message = {"GET_PROFILES": 0}

        return await self._send(message)

    async def get_profile_names(self):
        """Get profile names."""

        message = {"GET_PROFILE_NAMES": 0}

        return await self._send(message)

    async def get_timer_profiles(self):
        """Get timer profiles."""
        message = {"GET_PROFILE_TIMERS": 0}

        return await self._send(message)

    async def get_profile_0(self, device_name: str):
        """Get profile 0 from a device."""

        message = {"GET_PROFILE_0": device_name}

        return await self._send(message)

    async def get_timer_profile_0(self, device_name: str):
        """Get timer profile 0 from a device."""

        message = {"GET_TIMER_0": device_name}

        return await self._send(message)

    async def get_devices_data(self):
        """Return live data from hub and all devices."""

        # Get live data from Neohub
        live_hub_data = await self.get_live_data()

        # Get the engineers data from the Neohub for things like Device Type, Sensor Mode etc.
        eng_hub_data = await self.get_engineers()

        # Remove the devices node from the hub_data.
        devices = live_hub_data.devices
        delattr(live_hub_data, "devices")

        neo_devices = []  # Initialize the list to hold NeoStat devices

        for device in devices:
            # Find matching device ID in Engineers data
            for engineers_data_value in eng_hub_data.__dict__.values():
                # Check if there is a DEVICE_ID first (some devices may not have one, e.g. repeaters)
                device_id = getattr(device, "DEVICE_ID", None)
                engineer_device_id = getattr(engineers_data_value, "DEVICE_ID", None)

                if device_id is None or engineer_device_id is None:
                    self._logger.debug(
                        "Ignoring device '%s', which has no ID and might be a repeater.",
                        device.device,
                    )
                elif device_id == engineer_device_id:
                    for x in engineers_data_value.__dict__.items():
                        # Don't overwrite FLOOR_LIMIT, instead set ENG_FLOOR_LIMIT
                        if x[0] == "FLOOR_LIMIT":
                            setattr(device, "ENG_FLOOR_LIMIT", x[1])
                        else:
                            setattr(device, x[0], x[1])

            # Only append devices with a valid device_id
            device_id = getattr(device, "DEVICE_ID", None)
            if device_id is not None:
                neo_devices.append(NeoStat(self, device))

        # Prepare the final devices dictionary, excluding those without a valid device ID
        return {"neo_devices": neo_devices}

    async def get_all_live_data(self):
        """Return live data from hub and all devices."""

        # Get live data from Neohub
        live_hub_data = await self.get_live_data()

        # Remove the devices node from the hub_data.
        devices = live_hub_data.devices
        delattr(live_hub_data, "devices")

        keys_to_update = [
            k
            for k, v in self._update_timestamps.items()
            if getattr(live_hub_data, k, 0) != v
        ]

        profiles_updated = False
        timer_profiles_updated = False

        for k in keys_to_update:
            if k == "TIMESTAMP_ENGINEERS":
                eng_result = await self.get_engineers()
                self._update_timestamps[k] = getattr(live_hub_data, k, 0)
                self._eng_hub_data = {
                    getattr(device, "DEVICE_ID", None): device
                    for _, device in eng_result.__dict__.items()
                }

            if k == "TIMESTAMP_SYSTEM":
                system_result = await self.get_system()
                self._update_timestamps[k] = getattr(live_hub_data, k, 0)
                self._system_data = system_result

            if k in ("TIMESTAMP_PROFILE_0", "TIMESTAMP_PROFILE_COMFORT_LEVELS"):
                if not profiles_updated:
                    profiles_result = await self.get_profiles()
                    self._profiles = profiles_result
                    self._profiles = {
                        getattr(profile, "PROFILE_ID", None): profile
                        for _, profile in profiles_result.__dict__.items()
                    }
                    self._profiles_0 = {
                        getattr(device, "DEVICE_ID", None): await self.get_profile_0(
                            getattr(device, "ZONE_NAME", None)
                        )
                        for device in devices
                        if hasattr(device, "THERMOSTAT")
                        and hasattr(device, "ZONE_NAME")
                        and hasattr(device, "ACTIVE_PROFILE")
                        and not getattr(device, "OFFLINE", True)
                    }
                    profiles_updated = True
                self._update_timestamps[k] = getattr(live_hub_data, k, 0)

            if k in ("TIMESTAMP_PROFILE_TIMERS_0", "TIMESTAMP_PROFILE_TIMERS"):
                if not timer_profiles_updated:
                    timer_profiles_result = await self.get_timer_profiles()
                    self._timer_profiles = {
                        getattr(profile, "PROFILE_ID", None): profile
                        for _, profile in timer_profiles_result.__dict__.items()
                    }
                    self._timer_profiles_0 = {
                        getattr(
                            device, "DEVICE_ID", None
                        ): await self.get_timer_profile_0(
                            getattr(device, "ZONE_NAME", None)
                        )
                        for device in devices
                        if hasattr(device, "TIMECLOCK")
                        and hasattr(device, "ZONE_NAME")
                        and hasattr(device, "ACTIVE_PROFILE")
                        and not getattr(device, "OFFLINE", True)
                    }
                    timer_profiles_updated = True
                self._update_timestamps[k] = getattr(live_hub_data, k, 0)

            if k == "TIMESTAMP_DEVICE_LISTS":
                device_serial_numbers = await self.devices_sn()
                self._logger.debug("device serial numbers: %s", device_serial_numbers)
                # Convert device_serial_numbers (SimpleNamespace) to a dictionary
                device_serial_numbers_dict = vars(device_serial_numbers)
                self._device_sns = {
                    v[0]: {"name": k, "serial_number": v[1]}
                    for (k, v) in device_serial_numbers_dict.items()
                }
                self._device_sns = _validate_serial_numbers(self._device_sns)

                self._update_timestamps[k] = getattr(live_hub_data, k, 0)

        neo_devices = []  # Initialize the list to hold NeoStat devices

        for device in devices:
            # Check if there is a DEVICE_ID first (some devices may not have one, e.g. repeaters)
            device_id = getattr(device, "DEVICE_ID", None)
            if device_id:
                eng_device = self._eng_hub_data.get(device_id, None)
                # If any matching serials are found, assign the first one, else set to "UNKNOWN"
                serial_number = self._get_device_sn(device_id)

                # Add serial number if it doesn't already exist
                if getattr(device, "SERIAL_NUMBER", None) is None:
                    setattr(device, "SERIAL_NUMBER", serial_number)

                if eng_device:
                    for k, v in eng_device.__dict__.items():
                        if k == "FLOOR_LIMIT":
                            setattr(device, "ENG_FLOOR_LIMIT", v)
                        else:
                            setattr(device, k, v)
            if not device_id:
                # repeaters don't have a device id. Use the "device" attribute and set the device type
                repeater_name = getattr(device, "device", None)
                if repeater_name.startswith("repeaternode"):
                    setattr(device, "DEVICE_ID", repeater_name)
                    if getattr(device, "DEVICE_TYPE", None) is None:
                        setattr(device, "DEVICE_TYPE", 10)
                    if getattr(device, "SERIAL_NUMBER", None) is None:
                        setattr(device, "SERIAL_NUMBER", repeater_name)

            device_id = getattr(device, "DEVICE_ID", None)
            if device_id:
                neo_devices.append(NeoStat(self, device))

        return {
            ATTR_LIVE: live_hub_data,
            ATTR_DEVICES: neo_devices,
            ATTR_SYSTEM: self._system_data,
            ATTR_PROFILES: self._profiles,
            ATTR_PROFILES_0: self._profiles_0,
            ATTR_TIMER_PROFILES: self._timer_profiles,
            ATTR_TIMER_PROFILES_0: self._timer_profiles_0,
        }

    def _get_device_sn(self, device_id: int) -> str:
        """Get a device serial number by its device id."""

        return self._device_sns.get(device_id, {}).get(
            "serial_number", f"UNKNOWN-{device_id}"
        )

    async def disconnect(self) -> None:
        """Disconnect from the client."""
        if self._client:
            await self._client.disconnect()
            self._client = None


def _validate_serial_numbers(device_sns: dict) -> dict:
    duplicates = set()
    for device_id in sorted(device_sns.keys()):
        info = device_sns[device_id]
        sn = info["serial_number"]
        if sn in duplicates:
            info["serial_number"] = f"{sn}-{device_id}"
        else:
            duplicates.add(sn)
    return device_sns


class Client(ABC):
    """Base class for NeoHub clients."""

    def __init__(
        self,
        host: str,
        port: int,
        logger: logging.Logger,
        request_timeout: int = 60,
    ) -> None:
        """Initialize the client with connection parameters."""
        self._host = host
        self._port = port
        self._request_timeout = request_timeout
        self._logger = logger
        self.running = False

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the server."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the server."""

    @abstractmethod
    async def start(self) -> bool:
        """Start the client."""

    @abstractmethod
    async def send_message(self, message: dict | str) -> dict:
        """Send a message to the server and return the response."""


class WebSocketClient(Client):
    """WebSocket client for communication on port 4243."""

    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        logger: logging.Logger,
        request_timeout: int = 60,
    ) -> None:
        """Initialize WebSocket client with token and connection details."""
        super().__init__(host, port, logger, request_timeout)
        self._token = token
        self._websocket: websockets.WebSocketClientProtocol | None = None
        self._receive_task: asyncio.Task | None = None
        self._request_counter = itertools.count(start=1)
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._loop = asyncio.get_event_loop()
        self.mac_address: str | None = None

    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        uri = f"wss://{self._host}:{self._port}"
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self._websocket = await websockets.connect(
                uri,
                ssl=context,
                open_timeout=self._request_timeout,
                ping_interval=None,
            )
            self._logger.debug("WebSocket connected successfully")
            self.mac_address = None
            self._logger.info("Connected to %s", uri)
            self.running = True
        except Exception as e:
            self._logger.exception("Connection failed")
            raise NeoHubConnectionError from e
        else:
            return True

    async def receive_messages(self) -> None:
        """Handle incoming messages."""
        if not self._websocket:
            self._logger.error("WebSocket not initialized")
            return

        self._logger.debug("Starting receive task")
        try:
            while self.running:
                message = await self._websocket.recv()
                self._logger.debug("Received: %s", message)
                self._process_message(message)
        except ConnectionClosed:
            self._logger.warning("WebSocket connection closed")
            for future in self._pending_requests.values():
                if future.done():
                    continue
                future.set_exception(ConnectionError("WebSocket closed"))
            self._pending_requests.clear()
        except Exception:
            self._logger.exception("Error receiving message")
        finally:
            if self.running:
                self._logger.debug("Receive task ended, disconnecting")
                await self.disconnect()

    def _process_message(self, message: str) -> None:
        """Process individual message."""
        try:
            result = json.loads(message)
            command_id = result.get("command_id")
            if not command_id:
                self._logger.error("No command_id in response: %s", message)
                return

            future = self._pending_requests.get(command_id)
            if not future:
                self._logger.warning("Unexpected command_id: %s", command_id)
                return

            if result.get("message_type") != "hm_set_command_response":
                self._logger.error(
                    "Unexpected message_type: %s", result.get("message_type")
                )
                return

            del self._pending_requests[command_id]
            if not self.mac_address:
                self.mac_address = result.get("device_id")
                self._logger.debug("Set mac_address: %s", self.mac_address)

            future.set_result(result["response"])
        except json.JSONDecodeError:
            self._logger.exception("Failed to parse message as JSON")
        except Exception:
            self._logger.exception("Error processing message")

    async def send_message(self, message: dict | str) -> dict:
        """Send a message to the WebSocket server and return response."""
        if not self._websocket or not self.running:
            self._logger.error("WebSocket not connected")
            raise ConnectionError("WebSocket not connected")

        command_id = next(self._request_counter)
        encoded_message = json.dumps(
            {
                "message_type": "hm_get_command_queue",
                "message": json.dumps(
                    {
                        "token": self._token,
                        "COMMANDS": [
                            {"COMMAND": str(message), "COMMANDID": command_id}
                        ],
                    }
                ),
            }
        )
        self._logger.debug("Sending: %s", encoded_message)

        try:
            future = self._loop.create_future()
            self._pending_requests[command_id] = future
            await self._websocket.send(encoded_message)
            return await asyncio.wait_for(future, timeout=self._request_timeout)
        except TimeoutError:
            self._logger.error(
                "Request %s timed out after %ds", command_id, self._request_timeout
            )
            if command_id in self._pending_requests:
                del self._pending_requests[command_id]
            raise
        except Exception:
            self._logger.exception("Error sending message")
            if command_id in self._pending_requests:
                del self._pending_requests[command_id]
            raise

    async def start(self) -> bool:
        """Start the WebSocket client."""
        if await self.connect():
            self._receive_task = asyncio.create_task(self.receive_messages())
            self._receive_task.add_done_callback(self._handle_receive_task_done)
            self._logger.debug("WebSocket client started")
            return True
        return False

    def _handle_receive_task_done(self, task: asyncio.Task) -> None:
        """Handle completion of receive task."""
        try:
            task.result()
        except asyncio.CancelledError:
            self._logger.debug("Receive task cancelled")
        except Exception:
            self._logger.exception("Receive task failed")
        finally:
            if self.running:
                self._logger.debug("Receive task ended unexpectedly, disconnecting")
                self._loop.create_task(self.disconnect())

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        self.running = False
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                self._logger.debug("Receive task cancellation completed")
        if self._websocket:
            try:
                await self._websocket.close()
                self._logger.info("WebSocket disconnected")
            except Exception:
                self._logger.exception("Error during disconnect")
        self._receive_task = None
        self._websocket = None


class LegacyClient(Client):
    """TCP client for legacy communication on port 4242 with persistent connection."""

    def __init__(
        self,
        host: str,
        port: int,
        logger: logging.Logger,
        request_timeout: int = 60,
    ) -> None:
        """Initialize TCP client with connection details."""
        super().__init__(host, port, logger, request_timeout)
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Establish a persistent TCP connection."""
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port
            )
            self._logger.debug("TCP connection established")
            self._logger.info("Connected to %s:%s", self._host, self._port)
            self.running = True
        except Exception as e:
            self._logger.exception("Connection failed")
            raise NeoHubConnectionError from e
        else:
            return True

    async def send_message(self, message: dict | str) -> dict:
        """Send a message to the TCP server and return the response."""
        if not self._writer or not self._reader or not self.running:
            self._logger.error("TCP connection not established")
            raise ConnectionError("TCP connection not established")

        async with self._lock:
            try:
                encoded_message = bytearray(json.dumps(message) + "\0\r", "utf-8")
                self._logger.debug("Sending: %s", encoded_message)
                self._writer.write(encoded_message)
                await self._writer.drain()

                data = await asyncio.wait_for(
                    self._reader.readuntil(b"\0"), timeout=self._request_timeout
                )
                json_string = data.decode("utf-8").strip("\0")
            except TimeoutError:
                self._logger.exception(
                    "Request timed out after %ds", self._request_timeout
                )
                await self.disconnect()
                raise
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                self._logger.exception("Connection lost during send")
                await self.disconnect()
                raise ConnectionError("TCP connection lost") from e
            except json.JSONDecodeError as e:
                self._logger.exception("Failed to parse response as JSON")
                await self.disconnect()
                raise NeoHubConnectionError("Invalid JSON response") from e
            except Exception as e:
                self._logger.exception("Error sending message")
                await self.disconnect()
                raise NeoHubConnectionError from e
            else:
                return json_string

    async def start(self) -> bool:
        """Start the Legacy client."""
        return await self.connect()

    async def disconnect(self) -> None:
        """Disconnect from the TCP server."""
        self.running = False
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info("TCP connection disconnected")
            except Exception:
                self._logger.exception("Error during disconnect")
        self._reader = None
        self._writer = None
