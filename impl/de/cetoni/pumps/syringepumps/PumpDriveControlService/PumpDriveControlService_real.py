"""
________________________________________________________________________

:PROJECT: sila_cetoni

*Pump Drive Control Service*

:details: PumpDriveControlService:
    Functionality to control and maintain the drive that drives the pump.
    Allows to initialize a pump (e.g. by executing a reference move) and obtain status information about the pump
    drive's current state (i.e. enabled/disabled).
    The initialization has to be successful in order for the pump to work correctly and dose fluids. If the
    initialization fails, the DefinedExecutionError InitializationFailed is thrown.

:file:    PumpDriveControlService_real.py
:authors: Florian Meinicke

:date: (creation)          2019-07-16T11:11:31.282215
:date: (last modification) 2021-07-11T07:37:44.231684

.. note:: Code generated by sila2codegenerator 0.3.6

________________________________________________________________________

**Copyright**:
  This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
  INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

  For further Information see LICENSE file that comes with this distribution.
________________________________________________________________________
"""

__version__ = "0.1.0"

# import general packages
import logging
import time         # used for observables
import uuid         # used for observables
import grpc         # used for type hinting only

from configparser import ConfigParser, NoSectionError, NoOptionError

# import qmixsdk
from qmixsdk import qmixbus
from qmixsdk import qmixpump

# import SiLA2 library
import sila2lib.framework.SiLAFramework_pb2 as silaFW_pb2

# import SiLA errors
from impl.common.errors import DeviceError, SiLAExecutionError

# import gRPC modules for this feature
from .gRPC import PumpDriveControlService_pb2 as PumpDriveControlService_pb2
# from .gRPC import PumpDriveControlService_pb2_grpc as PumpDriveControlService_pb2_grpc

# import default arguments
from .PumpDriveControlService_default_arguments import default_dict

# import SiLA Defined Error factories
from .PumpDriveControlService_defined_errors import InitializationFailedError

from application.system import ApplicationSystem, SystemState

# noinspection PyPep8Naming,PyUnusedLocal
class PumpDriveControlServiceReal:
    """
    Implementation of the *Pump Drive Control Service* in *Real* mode
        This is a sample service for controlling neMESYS syringe pumps via SiLA2
    """

    def __init__(self, pump: qmixpump.Pump, sila2_conf: ConfigParser):
        """Class initialiser"""

        logging.debug('Started server in mode: {mode}'.format(mode='Real'))

        self.pump = pump
        self.sila2_conf = sila2_conf
        self.system = ApplicationSystem()

        self._restore_last_drive_position_counter()

    def _restore_last_drive_position_counter(self):
        """
        Reads the last drive position counter from the server's config file.
        """
        pump_name = self.pump.get_pump_name()
        try:
            drive_pos_counter = int(self.sila2_conf[pump_name]["drive_pos_counter"])
            logging.debug("Restoring drive position counter: %d", drive_pos_counter)
            self.pump.restore_position_counter_value(drive_pos_counter)
        except NoSectionError as err:
            logging.error("No section for %s in SiLA2 config file: %s", pump_name, err)
        except (NoOptionError, KeyError) as err:
            logging.error("Cannot read config file option in %s", err)
            logging.error("No drive position counter found! Reference move needed!")


    def _wait_calibration_finished(self, timeout_sec):
        """
        The function waits until pump calibration has finished or
        until the timeout occurs.
        """
        timer = qmixbus.PollingTimer(timeout_sec * 1000)
        result = False
        while not (result or timer.is_expired()):
            time.sleep(0.1)
            result = self.pump.is_calibration_finished()
        return result


    def InitializePumpDrive(self, request, context: grpc.ServicerContext) \
            -> PumpDriveControlService_pb2.InitializePumpDrive_Responses:
        """
        Executes the unobservable command "Initialize Pump Drive"
            Initialize the pump drive (e.g. by executing a reference move).

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        self.pump.calibrate()
        time.sleep(0.2)
        try:
            calibration_finished = self._wait_calibration_finished(60)
        except DeviceError as err:
            raise InitializationFailedError(f'QmixSDK returned the following error: {err}')

        logging.info("Pump calibrated: %s", calibration_finished)
        last_error = self.pump.read_last_error()
        if not calibration_finished and last_error.code != 0:
            raise InitializationFailedError(f'The last error that occurred was {last_error}')


        return PumpDriveControlService_pb2.InitializePumpDrive_Responses()

    def EnablePumpDrive(self, request, context: grpc.ServicerContext) \
            -> PumpDriveControlService_pb2.EnablePumpDrive_Responses:
        """
        Executes the unobservable command "Enable Pump Drive"
            Set the pump into enabled state.

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        if self.pump.is_in_fault_state():
            self.pump.clear_fault()
        self.pump.enable(True)

        return PumpDriveControlService_pb2.EnablePumpDrive_Responses()

    def DisablePumpDrive(self, request, context: grpc.ServicerContext) \
            -> PumpDriveControlService_pb2.DisablePumpDrive_Responses:
        """
        Executes the unobservable command "Disable Pump Drive"
            Set the pump into disabled state.

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        self.pump.enable(False)

        return PumpDriveControlService_pb2.DisablePumpDrive_Responses()

    def Subscribe_PumpDriveState(self, request, context: grpc.ServicerContext) \
            -> PumpDriveControlService_pb2.Subscribe_PumpDriveState_Responses:
        """
        Requests the observable property Pump Drive State
            The current state of the pump. This is either 'Enabled' or 'Disabled'. Only if the sate is 'Enabled', the pump can dose fluids.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            PumpDriveState (Pump Drive State): The current state of the pump. This is either 'Enabled' or 'Disabled'. Only if the sate is 'Enabled', the pump can dose fluids.
        """

        logging.debug("Pump is enabled: %s", self.pump.is_enabled())

        while True:
            yield PumpDriveControlService_pb2.Subscribe_PumpDriveState_Responses(
                PumpDriveState=silaFW_pb2.String(
                    value='Enabled' if self.system.state.is_operational() and self.pump.is_enabled() else 'Disabled'
                )
            )

            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.5)


    def Subscribe_FaultState(self, request, context: grpc.ServicerContext) \
            -> PumpDriveControlService_pb2.Subscribe_FaultState_Responses:
        """
        Requests the observable property Fault State
            Returns if the pump is in fault state. If the value is true (i.e. the pump is in fault state), it can be cleared by calling EnablePumpDrive.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            FaultState (Fault State): Returns if the pump is in fault state. If the value is true (i.e. the pump is in fault state), it can be cleared by calling EnablePumpDrive.
        """

        logging.debug("Pump is in fault state: %s", self.pump.is_in_fault_state())

        while True:
            yield PumpDriveControlService_pb2.Subscribe_FaultState_Responses(
                FaultState=silaFW_pb2.Boolean(value=self.pump.is_in_fault_state())
            )

            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.5)
