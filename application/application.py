"""
________________________________________________________________________

:PROJECT: sila_cetoni

*Application*

:details: Application:
    The main application class containing all logic of the sila_cetoni.py

:file:    application.py
:authors: Florian Meinicke

:date: (creation)          2021-07-19
:date: (last modification) 2021-07-15

________________________________________________________________________

**Copyright**:
  This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
  INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

  For further Information see LICENSE file that comes with this distribution.
________________________________________________________________________
"""

import os
import sys
import time
import logging
import argparse
from typing import List
from OpenSSL import crypto

from . import CETONI_SDK_PATH
# adjust PATH variable to point to the SDK
sys.path.append(CETONI_SDK_PATH)
sys.path.append(os.path.join(CETONI_SDK_PATH, "lib", "python"))

# only used for type hinting
from sila2lib.sila_server import SiLA2Server
from qmixsdk import qmixpump

from .system import ApplicationSystem
from .singleton import Singleton

DEFAULT_BASE_PORT = 50052

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Application(metaclass=Singleton):
    """
    Encompasses the main application logic
    """

    system: ApplicationSystem

    key_cert_path: str
    base_port: int
    servers: List[SiLA2Server]

    def __init__(self, device_config_path: str = "",
                 base_port: int = DEFAULT_BASE_PORT):
        if not device_config_path:
            return

        self.system = ApplicationSystem(device_config_path)
        self._generate_self_signed_cert()

        self.base_port = base_port
        logging.debug("Creating SiLA 2 servers...")
        self.servers = self.create_servers()

    def _generate_self_signed_cert(self):
        """
        Generates a self-signed SSL key/certificate pair on the fly
        """

        self.key_cert_path = os.path.join(os.path.dirname(__file__), '..', '.ssl', 'sila_cetoni.{}')
        os.makedirs(os.path.dirname(self.key_cert_path), exist_ok=True)

        private_key = crypto.PKey()
        private_key.generate_key(crypto.TYPE_RSA, 4096)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = 'DE'
        cert.get_subject().ST = 'TH'
        cert.get_subject().O = 'CETONI'
        cert.get_subject().CN = 'SiLA2'
        cert.set_serial_number(1)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)
        cert.set_issuer(cert.get_subject())

        cert.set_pubkey(private_key)
        cert.sign(private_key, 'sha512') # signing certificate with public key

        # writing key / cert pair
        with open(self.key_cert_path.format('crt'), "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
        with open(self.key_cert_path.format('key'), "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key).decode("utf-8"))

    def run(self):
        """
        Run the main application loop

        Starts the whole system (i.e. all devices) and all SiLA 2 servers
        Runs until Ctrl-C is pressed on the command line or `stop()` has been called
        """
        self.system.start()

        self.start_servers()

        print("Press Ctrl-C to stop...", flush=True)
        try:
            while not self.system.state.shutting_down():
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            print()
            self.stop()

    def stop(self):
        """
        Stops the application

        Shuts down all SiLA 2 servers and stops the whole system
        """
        self.stop_servers()
        self.system.stop()

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

    def create_servers(self):
        """
        Creates a corresponding SiLA 2 server for every device connected to the bus
        """

        servers = []
        # common args for all servers
        args = argparse.Namespace(
            server_port=self.base_port-1,
            server_type="TestServer",
            encryption_key=self.key_cert_path.format('key'),
            encryption_cert=self.key_cert_path.format('crt'),
            meta_dir=None
        )

        #---------------------------------------------------------------------
        # pumps
        for pump in self.system.pumps:
            args.server_port += 1
            args.server_name = pump.name.replace("_", " ")
            args.description = "Allows to control a {contiflow_descr}neMESYS syringe pump".format(
                contiflow_descr="contiflow pump made up of two " if isinstance(pump, qmixpump.ContiFlowPump) else ""
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
        for axis_system in self.system.axis_systems:
            args.server_port += 1
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
        for valve_device in self.system.valves:
            args.server_port += 1
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
        for controller_device in self.system.controller_devices:
            args.server_port += 1
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
        for io_device in self.system.io_devices:
            args.server_port += 1
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
