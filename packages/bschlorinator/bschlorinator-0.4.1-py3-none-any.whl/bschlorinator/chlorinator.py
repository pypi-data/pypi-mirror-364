import asyncio
import itertools
import logging
import time
from logging import Logger

from serial import Serial
from collections import defaultdict

import platform

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    if platform.machine().startswith("arm"):
        raise  # Fails if on Raspberry Pi
    else:
        from unittest.mock import MagicMock
        GPIO = None


from . import const


class SerialResponseParser:

    def __init__(self, response: bytes, multiplier, parser):
        self.response = response
        self.multiplier = multiplier
        self.parser = parser

    def parse(self):
        data_list = list(self.response)
        return self.parser(data_list, self.multiplier)

    def __str__(self):
        return f"<SerialResponseParser response={self.response} multiplier={self.multiplier} parser={self.parser}>"

    def __repr__(self):
        return f"<SerialResponseParser response={self.response} multiplier={self.multiplier} parser={self.parser}>"

class RelayController:

    def __init__(self, port: Serial, logger: Logger, chlorinator: 'BSChlorinator'):
        self.logger = logger
        self.port = port
        self.chlorinator = chlorinator
        self._relays = defaultdict(dict)

    @property
    def relays(self):
        return self._relays

    @relays.setter
    def relays(self, kv):
        key, value = kv
        self._relays[key] = value

    async def relay_on(self, nr: int):
        """Powers relay 0-3 manually on"""
        if not 0 <= nr <= 3:
            raise ValueError("Relay number must be between 0 and 3")
        relays_on = [b"R\xfd\4", b"R\xf7\4", b"R\xdf\4", b"R\x7f\4"]
        code = relays_on[nr]
        await self.chlorinator.send_simple(code, priority=0, repeat=3)

    async def relay_off(self, nr: int):
        """Powers relay 0-3 manually off"""
        if not 0 <= nr <= 3:
            raise ValueError("Relay number must be between 0 and 3")
        relays_off = [b"R\xfc\4", b"R\xf3\4", b"R\xcf\4", b"R\x3f\4"]
        code = relays_off[nr]
        await self.chlorinator.send_simple(code, priority=0, repeat=3)

    async def set_auto_mode(self, relay_nr: int):
        """Set relay to auto mode"""
        if not 0 <= relay_nr <= 3:
            raise ValueError("Relay number must be between 0 and 3")
        auto_mode_codes = [b"R\xfe\x04", b"R\xfb\x04", b"R\xef\x04", b"R\xbf\x04"]
        code = auto_mode_codes[relay_nr]
        await self.chlorinator.send_simple(code, priority=0, repeat=3)
        self.logger.info(f"Relay {relay_nr} set to auto mode")

    @staticmethod
    def _make_read_command(relay_nr: int, is_start: bool, slot: int = 1) -> bytes:
        base = 0xC9 + (relay_nr * 8) + ((slot - 1) * 2)
        code = base if is_start else base + 1
        return bytes([0x3f, code, 0x04])  # b'\x3f\xc9\x04' z. B.

    @staticmethod
    def _make_write_command(relay_nr: int, is_start: bool, hour: int, minute: int, slot: int = 1) -> bytes:
        base = 0xC9 + (relay_nr * 8) + ((slot - 1) * 2)
        code = base if is_start else base + 1
        return bytes([code, minute, hour])  # b'\xc9\x1E\x0A' z. B.

    async def read_program(self, relay_nr: int, slot: int = 1) -> tuple[str, str] | None:
        try:
            start_cmd = self._make_read_command(relay_nr, is_start=True, slot=slot)
            stop_cmd = self._make_read_command(relay_nr, is_start=False, slot=slot)

            start_resp = await self.chlorinator.send_and_receive(start_cmd, priority=0)
            stop_resp = await self.chlorinator.send_and_receive(stop_cmd, priority=0)

            if len(start_resp) < 3 or len(stop_resp) < 3:
                self.logger.warning("Invalid program response for relay %s", relay_nr)
                return None

            start_time = f"{start_resp[2]:02}:{start_resp[1]:02}"
            stop_time = f"{stop_resp[2]:02}:{stop_resp[1]:02}"
            return start_time, stop_time
        except Exception as e:
            self.logger.exception(f"Failed to read program for relay {relay_nr}: {e}")
            return None

    async def write_program(self, relay_nr: int, start: str, stop: str, slot: int = 1):
        try:
            start_hour, start_min = map(int, start.split(":"))
            stop_hour, stop_min = map(int, stop.split(":"))

            start_cmd = self._make_write_command(relay_nr, is_start=True, hour=start_hour, minute=start_min, slot=slot)
            stop_cmd = self._make_write_command(relay_nr, is_start=False, hour=stop_hour, minute=stop_min, slot=slot)
            self.logger.debug(f'Start: {start_cmd}, Stop: {stop_cmd}')
            await self.set_auto_mode(relay_nr)  # Relay to AUTO mode
            response_start = await self.chlorinator.send_simple(start_cmd, repeat=3, priority=0)
            response_end = await self.chlorinator.send_simple(stop_cmd, repeat=3, priority=0)
            self.logger.debug(f'Start response: {response_start}, End response: {response_end}')
            self.logger.info(f"Program for relay {relay_nr} set: {start} - {stop}")
        except Exception as e:
            self.logger.exception(f"Failed to write program for relay {relay_nr}: {e}")

    async def update_relays_data(self, priority=1):
        """Reads status of all 4 relays (4 Bytes expected)"""
        response = await self.chlorinator.send_and_receive(const.relay_status_command, priority=priority)
        self.logger.debug(f"Response for relays status: {response}")
        if len(response) < 2 or response[0] != ord("R"):
            self.logger.warning("Invalid relay response!")
            return
        relays_status, relays_mode = SerialResponseParser(response, 1, const.bit_parser).parse()
        relays_times = await asyncio.gather(*[self.read_program(n) for n in range(len(const.relay_names))])
        for i in range(len(const.relay_names)):
            relay = {
                'is_active': relays_status[i],
                'automatic': relays_mode[i],
                'times': relays_times[i]
            }
            self.relays[const.relay_names[i]] = relay
            self.chlorinator.sensor_data[const.RELAYS][const.relay_names[i]] = self.relays[const.relay_names[i]]

class BSChlorinator:
    relay_controller: RelayController
    # Status constants
    STATUS_CONNECTED = 'Connected'
    STATUS_UNREACHABLE = 'Unreachable'
    STATUS_ERROR = 'Error'

    def __init__(self, port: Serial, gpio_pin: int = 37, channel: int = 1, logger:logging.Logger = None):
        self.port = port
        self.gpio_pin = gpio_pin
        self.channel = channel
        self._logger = logger
        self._sensor_data = defaultdict(str)
        self._loop_restarts = 0
        self._init_gpio()
        self.status = self.STATUS_CONNECTED
        self.command_queue = asyncio.PriorityQueue()
        self._counter = itertools.count()
        self._worker_task = asyncio.create_task(self._serial_worker())

        self.relay_controller = RelayController(self.port, self._logger, self)
        # Set initial values
        self.sensor_data[const.RELAYS] = self.relay_controller.relays

    @property
    def sensor_data(self):
        return self._sensor_data

    @sensor_data.setter
    def sensor_data(self, kv):
        key, value = kv
        self._sensor_data[key] = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @property
    def channel(self) -> int:
        return self._channel

    @channel.setter
    def channel(self, value: int):
        self._channel = value - 1

    @property
    def loop_restarts(self) -> int:
        return self._loop_restarts

    @loop_restarts.setter
    def loop_restarts(self, value: int):
        self._loop_restarts = value

    def clear_buffer(self):
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()

    def _init_gpio(self):
        """Init GPIO"""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)

    async def _configure_serial(self) -> None:
        """Configures serial port and channel to send on"""
        channel_cmd = f"ATS200={self.channel}"
        commands = [
            channel_cmd,
            "ATS201=1",
            "ATS202=7",
            "ATS250=2",
            "ATS252=1",
            "ATS255=0",
            "ATS256=2",
            "ATS258=1",
            "ATS296=1"
        ]
        self.clear_buffer()
        await asyncio.sleep(1)

        # Set serial to a command mode
        self.port.write(b"+++")
        await asyncio.sleep(1)

        for cmd in commands:
            self._logger.info(f"Sending: {cmd}")
            self.port.write((cmd + "\x0d").encode())
            await asyncio.sleep(1)
        # Set serial back to data mode
        self.port.write(b'ATO\x0d')
        await asyncio.sleep(1)

    async def _reset_serial_module(self) -> None:
        """Reset serial module"""
        GPIO.output(self.gpio_pin, GPIO.LOW)
        await asyncio.sleep(3)
        GPIO.output(self.gpio_pin, GPIO.HIGH)
        await asyncio.sleep(1)

    async def _config_channel(self) -> None:
        """Configuration of channel for serial port"""
        channel_cmd = f'ATS200={self.channel}'
        self.clear_buffer()
        await asyncio.sleep(1)

        # Set serial to a command mode
        self.port.write(b'+++')
        await asyncio.sleep(1)
        self.port.write((channel_cmd + '\x0d').encode())
        await asyncio.sleep(1)
        # Get back to data mode
        self.port.write('ATO\x0d'.encode())
        await asyncio.sleep(1)

    async def _serial_worker(self):
        while True:
            priority, counter, data, fut = await self.command_queue.get()
            try:
                self.port.write(data)
                await asyncio.sleep(0.15)
                if fut:
                    fut.set_result(self._read_cr())
            except Exception as e:
                if fut:
                    fut.set_exception(e)
            finally:
                self.command_queue.task_done()

    def _read_cr(self, max_length: int = 256, timeout: float = 3.0) -> bytes:
        """Reads bytes from a serial port and returns results as a list"""
        self.port.timeout = timeout
        read_value = self.port.read(size=3)
        return read_value

    async def send_simple(self, data: bytes, priority: int = 1, repeat=1):
        for i in range(repeat):
            await self.command_queue.put((priority, next(self._counter), data, None))

    async def send_and_receive(self, data: bytes, priority: int = 1) -> bytes:
        fut = asyncio.get_running_loop().create_future()

        await self.command_queue.put((priority, next(self._counter), data, fut))
        return await fut

    async def _update_sensor_data(self) -> None:
        """Reads and updates data of the chlorinator sensor"""
        # Clear buffer to prevent wrong values
        self.clear_buffer()
        zipped_sensors = zip(const.keys, const.commands, const.multipliers, const.parsers)
        for key, command, multiplier, parser in zipped_sensors:
            response = await self.send_and_receive(command)
            if len(response) < 1:
                self.status = self.STATUS_UNREACHABLE
                self.sensor_data[key] = None
            else:
                self.status = self.STATUS_CONNECTED
                self.sensor_data[key] = SerialResponseParser(response, multiplier, parser).parse()
        # Update timestamp
        self.sensor_data['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.sensor_data['pool_restarts'] = str(self.loop_restarts)
        self.sensor_data['status'] = self.status

    async def sensor_loop(self):
        await self._reset_serial_module()
        self._logger.info('bschlorinator restarted')
        await self._config_channel()
        self._logger.info('bschlorinator channel configured')
        while True:
            self._logger.info('entering sensor pool loop')
            try:
                async with asyncio.timeout(40):
                    await self._update_sensor_data()
                    await self.relay_controller.update_relays_data()
            except asyncio.TimeoutError:
                self._logger.error('sensor pool loop timeout exception occurred')
                await self._reset_serial_module()
                await self._config_channel()
                self.loop_restarts += 1


