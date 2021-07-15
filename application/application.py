"""
________________________________________________________________________

:PROJECT: sila_cetoni

*Application*

:details: Application:
    The main application class containing all logic of the sila_cetoni.py

:file:    application.py
:authors: Florian Meinicke

:date: (creation)          2021-07-15
:date: (last modification) 2021-07-15

________________________________________________________________________

**Copyright**:
  This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
  INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

  For further Information see LICENSE file that comes with this distribution.
________________________________________________________________________
"""

import sys
import time
import logging
import threading
import argparse
from typing import List

# only used for type hinting
from sila2lib.sila_server import SiLA2Server

# import qmixsdk
from qmixsdk import qmixbus, qmixpump, qmixcontroller, qmixanalogio, qmixdigio, qmixmotion, qmixvalve

from .device import DeviceConfiguration, Device, PumpDevice, AxisSystemDevice, \
                    ValveDevice, ControllerDevice, IODevice

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Application:
    """
    Encompasses the main application logic
    """

    device_config: DeviceConfiguration
    bus: qmixbus.Bus

    pumps: List[PumpDevice]
    axis_systems: List[AxisSystemDevice]
    valves: List[ValveDevice]
    controllers: List[ControllerDevice]
    io_devices: List[IODevice]

    servers: List[SiLA2Server]

    system_operational: bool
    shutting_down: bool

    def __init__(self, device_config_path: str):
        self.device_config = DeviceConfiguration(device_config_path)

        self.bus = qmixbus.Bus()
        self.open_bus()

        self.controller_devices = []
        self.io_devices = []
        self.valve_devices = []

        logging.debug("Looking up devices...")
        # The order is important here! Many devices have I/O channels but are not
        # pure I/O devices (similarly, pumps might have a valve but they're not a
        # valve device). That's why valves have to be detected after pumps and I/O
        # devices have to be detected last (since then we can guarantee that there
        # is no possibility for an I/O channel to belong to an I/O device).
        self.pumps = self.get_availabe_pumps()
        self.axis_systems = self.get_availabe_axis_systems()
        self.valves = self.get_availabe_valves()
        self.controller_devices = self.get_availabe_controllers()
        self.io_devices = self.get_availabe_io_channels()

        logging.debug(f"Pumps: {repr(self.pumps)}")
        logging.debug(f"axis: {repr(self.axis_systems)}")
        logging.debug(f"valve devices: {repr(self.valves)}")
        logging.debug(f"controller devices: {repr(self.controller_devices)}")
        logging.debug(f"io devices: {repr(self.io_devices)}")

        logging.debug("Creating SiLA 2 servers...")
        self.servers = self.create_servers()

        self.system_operational = True
        self.shutting_down = False

    def run(self):
        """
        Run the main application loop

        Starts the CAN bus communications and the bus monitoring
        Starts all SiLA 2 servers
        Runs until Ctrl-C is pressed on the command line or `stop()` has been called
        """
        logging.debug("Starting bus and enabling devices...")
        self.bus.start()
        self.enable_pumps()
        self.enable_axis_systems()

        self._start_bus_monitoring()

        self.start_servers()

        print("Press Ctrl-C to stop...")
        try:
            while not self.shutting_down:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            print()
            self.stop()

    def stop(self):
        """
        Stops the application

        Stops all SiLA 2 servers
        Stops the CAN bus monitoring and the bus communication
        """
        self.shutting_down = True
        self.stop_servers()
        self.stop_and_close_bus()

    def start_servers(self):
        """
        Starts all SiLA 2 servers
        """
        logging.debug("Starting SiLA 2 servers...")
        for server in self.servers:
            server.run(block=False)
        logging.info("All servers started!")

    def stop_servers(self):
        """
        Stops all SiLA 2 servers
        """
        logging.debug("Shutting down servers...")
        for server in self.servers:
            server.stop_grpc_server()
        logging.info("Done!")

    def _start_bus_monitoring(self):
        """
        Starts monitoring the CAN bus for events (esp. emergency and error events)
        """
        self.monitoring_thread = threading.Thread(target=self.monitor_events)
        self.monitoring_thread.start()


    #-------------------------------------------------------------------------
    # Bus
    def open_bus(self):
        """
        Opens the given device config and starts the bus communication
        """
        logging.debug("Opening bus...")
        try:
            self.bus.open(self.device_config.path, 0)
        except qmixbus.DeviceError as err:
            logging.error("Could not open the bus communication: %s", err)
            sys.exit(1)

    def stop_and_close_bus(self):
        """
        Stops and closes the bus communication
        """
        logging.debug("Closing bus...")
        self.bus.stop()
        self.bus.close()

    def monitor_events(self):
        """
        Runs an infinite loop that polls the bus for any events.

        If an emergency event is received that suggests that the controller was turned
        off (i.e. DC link under-voltage and a heartbeat error) all SiLA servers will
        be stopped.
        If a "heartbeat error resolved" event is received after the controller was turned
        off it is interpreted to mean that the controller is up and running again and
        the SiLA servers are attempted to start.
        """

        DC_LINK_UNDER_VOLTAGE = 0x3220

        def is_dc_link_under_voltage_event(event: qmixbus.Event):
            return event.event_id == qmixbus.EventId.device_emergency.value \
                and event.data[0] == DC_LINK_UNDER_VOLTAGE

        def is_heartbeat_err_occurred_event(event: qmixbus.Event):
            return event.event_id == qmixbus.EventId.device_guard.value \
                and event.data[0] == qmixbus.GuardEventId.heartbeat_err_occurred.value

        def is_heartbeat_err_resolved_event(event: qmixbus.Event):
            return event.event_id == qmixbus.EventId.device_guard.value \
                and event.data[0] == qmixbus.GuardEventId.heartbear_err_resolved.value

        self.system_operational = True

        while not self.shutting_down:
            time.sleep(1)

            event = self.bus.read_event()
            if not event.is_valid():
                continue
            logging.debug(f"event id: {event.event_id}, device: {event.device}, "
                          f"data: {event.data}, message: {event.string}")

            if self.system_operational and (is_dc_link_under_voltage_event(event) \
                or is_heartbeat_err_occurred_event(event)):
                self.system_operational = False

            if not self.system_operational and is_heartbeat_err_resolved_event(event):
                self.system_operational = True

    #-------------------------------------------------------------------------
    # Pumps
    def get_availabe_pumps(self) -> List[PumpDevice]:
        """
        Looks up all pumps from the current configuration and constructs a list of
        all found pumps

        :return: A list of all found pumps
        """
        pump_count = qmixpump.Pump.get_no_of_pumps()
        logging.debug("Number of pumps: %s", pump_count)

        pumps = []

        for i in range(pump_count):
            pump = qmixpump.Pump()
            pump.lookup_by_device_index(i)
            pump_name = pump.get_device_name()
            logging.debug("Found pump %d named %s", i, pump_name)
            try:
                pump.get_device_property(qmixpump.ContiFlowProperty.SWITCHING_MODE)
                pump = qmixpump.ContiFlowPump(pump.handle)
                logging.debug("Pump %s is contiflow pump", pump_name)
            except qmixbus.DeviceError:
                pass
            pump_device = self.device_config.device_by_name(pump_name)
            PumpDevice.convert_to_class(pump_device, handle=pump.handle)
            pumps += [pump_device]

        return pumps

    def enable_pumps(self):
        """
        Enables all pumps
        """
        for pump in self.pumps:
            if pump.is_in_fault_state():
                pump.clear_fault()
            if not pump.is_enabled():
                pump.enable(True)

    #-------------------------------------------------------------------------
    # Motion Control
    def get_availabe_axis_systems(self) -> List[AxisSystemDevice]:
        """
        Looks up all axis systems connected to the bus

        :return: A list of all axis systems
        """

        system_count = qmixmotion.AxisSystem.get_axis_system_count()
        logging.debug("Number of axis systems: %s", system_count)

        axis_systems = []

        for i in range(system_count):
            axis_system = qmixmotion.AxisSystem()
            axis_system.lookup_by_device_index(i)
            axis_system_name = axis_system.get_device_name()
            logging.debug("Found axis system %d named %s", i, axis_system.get_device_name())
            axis_system_device = self.device_config.device_by_name(axis_system_name)
            AxisSystemDevice.convert_to_class(axis_system_device, handle=axis_system.handle)
            axis_systems += [axis_system_device]

        return axis_systems

    def enable_axis_systems(self):
        """
        Enables all axis systems
        """
        for axis_system in self.axis_systems:
            axis_system.enable(True)

    #-------------------------------------------------------------------------
    # Valves
    def get_availabe_valves(self) -> List[ValveDevice]:
        """
        Looks up all valves from the current configuration and maps them to their
        corresponding device

        :return: A list of all valves
        """

        valve_count = qmixvalve.Valve.get_no_of_valves()
        logging.debug("Number of valves: %s", valve_count)

        valves = []

        for i in range(valve_count):
            valve = qmixvalve.Valve()
            valve.lookup_by_device_index(i)
            try:
                valve_name = valve.get_device_name()
            except OSError:
                # When there are contiflow pumps in the config the corresponding
                # valves from the original syringe pumps are duplicated internally.
                # I.e. with one contiflow pump made up of two low pressure pumps
                # with their corresponding valves the total number of valves is
                # 4 despite of the actual 2 physical valves available. This leads
                # to an access violation error inside QmixSDK in case the device
                # name of one of the non-existent contiflow valves is requested.
                # We can fortunately mitigate this with this try-except here.
                continue
            logging.debug("Found valve %d named %s", i, valve_name)

            for device in self.device_config.devices:
                if device.name.rsplit('_Pump', 1)[0] in valve_name:
                    logging.debug(f"Valve {valve_name} belongs to device {device}")
                    if 'QmixIO' in device.name:
                        # These valve devices are actually just convenience devices
                        # that operate on digital I/O channels. Hence, they can be
                        # just used via their corresponding I/O channel.
                        continue
                    device.valves += [valve]
                    if type(device) == Device:
                        ValveDevice.convert_to_class(device)
                        valves += [device]
        return valves

    #-------------------------------------------------------------------------
    # Controllers
    def get_availabe_controllers(self) -> List[ControllerDevice]:
        """
        Looks up all controller channels from the current configuration and maps
        them to their corresponding device

        :return: A list of all controller devices
        """
        channel_count = qmixcontroller.ControllerChannel.get_no_of_channels()
        logging.debug("Number of controller channels: %s", channel_count)

        channels = []

        for i in range(channel_count):
            channel = qmixcontroller.ControllerChannel()
            channel.lookup_channel_by_index(i)
            logging.debug("Found controller channel %d named %s", i, channel.get_name())
            channels.append(channel)

        return self.device_config.add_channels_to_device(channels)

    #-------------------------------------------------------------------------
    # I/O
    def get_availabe_io_channels(self) -> List[IODevice]:
        """
        Looks up all analog and digital I/O channels from the current configuration
        and maps them to their corresponding device

        :return: A list of all I/O channels
        """

        channels = []

        for (description, ChannelType) in {
            'analog in': qmixanalogio.AnalogInChannel,
            'analog out': qmixanalogio.AnalogOutChannel,
            'digital in': qmixdigio.DigitalInChannel,
            'digital out': qmixdigio.DigitalOutChannel}.items():

            channel_count = ChannelType.get_no_of_channels()
            logging.debug("Number of %s channels: %s", description, channel_count)

            for i in range(channel_count):
                channel = ChannelType()
                channel.lookup_channel_by_index(i)
                channel_name = channel.get_name()
                logging.debug("Found %s channel %d named %s", description, i, channel_name)
                channels.append(channel)

        return self.device_config.add_channels_to_device(channels)

    #-------------------------------------------------------------------------
    # SiLA 2
    def create_servers(self):
        """
        Creates a corresponding SiLA 2 server for every device connected to the bus
        """

        servers = []
        # common args for all servers
        args = argparse.Namespace(
            port=50051, # base port
            server_type="TestServer",
            encryption_key=None,
            encryption_cert=None
        )

        #---------------------------------------------------------------------
        # pumps
        for pump in self.pumps:
            args.port += 1
            args.server_name = pump.name.replace("_", " ")
            args.description = "Allows to control a {contiflow_descr} neMESYS syringe pump".format(
                contiflow_descr="contiflow pump made up of two" if isinstance(pump, qmixpump.ContiFlowPump) else ""
            )

            if isinstance(pump, qmixpump.ContiFlowPump):
                from serv.pumps.contiflowpumps.Contiflow_server import ContiflowServer
                server = ContiflowServer(
                    cmd_args=args,
                    qmix_pump=pump,
                    simulation_mode=False
                )
            else:
                from serv.pumps.syringepumps.neMESYS_server import neMESYSServer
                server = neMESYSServer(
                    cmd_args=args,
                    qmix_pump=pump,
                    valve=pump.valves[0] if pump.valves else None,
                    io_channels=pump.io_channels,
                    simulation_mode=False
                )
            servers += [server]

        #---------------------------------------------------------------------
        # axis systems
        for axis_system in self.axis_systems:
            args.port += 1
            args.server_name = axis_system.name.replace("_", " ")
            args.description = "Allows to control motion systems like axis systems"

            from serv.motioncontrol.MotionControl_server import MotionControlServer
            server = MotionControlServer(
                cmd_args=args,
                axis_system=axis_system,
                io_channels=axis_system.io_channels,
                device_properties=axis_system.properties,
                simulation_mode=False
            )
            servers += [server]

        #---------------------------------------------------------------------
        # valves
        for valve_device in self.valves:
            args.port += 1
            args.server_name = valve_device.name.replace("_", " ")
            args.description = "Allows to control valve devices"

            from serv.valves.Valve_server import ValveServer
            server = ValveServer(
                cmd_args=args,
                valves=valve_device.valves,
                simulation_mode=False
            )
            servers += [server]

        #---------------------------------------------------------------------
        # controller
        for controller_device in self.controller_devices:
            args.port += 1
            args.server_name = controller_device.name.replace("_", " ")
            args.description = "Allows to control Qmix Controller Channels"

            from serv.controllers.QmixControl_server import QmixControlServer
            server = QmixControlServer(
                cmd_args=args,
                controller_channels=controller_device.controller_channels,
                simulation_mode=False
            )
            servers += [server]

        #---------------------------------------------------------------------
        # I/O
        for io_device in self.io_devices:
            args.port += 1
            args.server_name = io_device.name.replace("_", " ")
            args.description = "Allows to control Qmix I/O Channels"

            from serv.io.QmixIO_server import QmixIOServer
            server = QmixIOServer(
                cmd_args=args,
                io_channels=io_device.io_channels,
                simulation_mode=False
            )
            servers += [server]

        return servers