"""
________________________________________________________________________

:PROJECT: SiLA2_python

*Force Monitoring Service*

:details: ForceMonitoringService:
    Functionality to control the force monitoring, read the force sensor and set a custom force limit for pump devices
    that support this functionality such as Nemesys S and Nemesys M.

:file:    ForceMonitoringService_real.py
:authors: Florian Meinicke

:date: (creation)          2021-11-30T07:38:43.941967
:date: (last modification) 2021-11-30T07:38:43.941967

.. note:: Code generated by sila2codegenerator 0.3.7

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
import math

# import SiLA2 library
import sila2lib.framework.SiLAFramework_pb2 as silaFW_pb2

# import SiLA errors
from impl.common.errors import SiLAFrameworkError, SiLAFrameworkErrorType, \
                               FlowRateOutOfRangeError, FillLevelOutOfRangeError, \
                               VolumeOutOfRangeError, SystemNotOperationalError

# import gRPC modules for this feature
from .gRPC import ForceMonitoringService_pb2 as ForceMonitoringService_pb2
# from .gRPC import ForceMonitoringService_pb2_grpc as ForceMonitoringService_pb2_grpc

# import default arguments
from .ForceMonitoringService_default_arguments import default_dict

# import qmixsdk
from qmixsdk import qmixbus, qmixpump

from application.system import ApplicationSystem, SystemState

# noinspection PyPep8Naming,PyUnusedLocal
class ForceMonitoringServiceReal:
    """
    Implementation of the *Force Monitoring Service* in *Real* mode
        This is a sample service for controlling neMESYS syringe pumps via SiLA2
    """

    def __init__(self, pump: qmixpump.Pump):
        """Class initialiser"""

        self.pump = pump
        self.system = ApplicationSystem()

        logging.debug('Started server in mode: {mode}'.format(mode='Real'))

    def __fully_qualified_command_id(self, command):
        """
        Returns the Fully Qualified Command Identifier for the given `command` of this Feature
        """
        return f"de.cetoni/pumps.syringepumps/ForceMonitoringService/v1/Command/{command}"

    def ClearForceSafetyStop(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.ClearForceSafetyStop_Responses:
        """
        Executes the unobservable command "Clear Force Safety Stop"
            Clear/acknowledge a force safety stop.

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        if not self.system.state.is_operational():
            raise SystemNotOperationalError(self.__fully_qualified_command_id('ClearForceSafetyStop'))

        self.pump.clear_force_safety_stop()

        return ForceMonitoringService_pb2.ClearForceSafetyStop_Responses()


    def EnableForceMonitoring(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.EnableForceMonitoring_Responses:
        """
        Executes the unobservable command "Enable Force Monitoring"
            Enable the force monitoring.

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        if not self.system.state.is_operational():
            raise SystemNotOperationalError(self.__fully_qualified_command_id('EnableForceMonitoring'))

        self.pump.enable_force_monitoring(True)

        return ForceMonitoringService_pb2.EnableForceMonitoring_Responses()


    def DisableForceMonitoring(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.DisableForceMonitoring_Responses:
        """
        Executes the unobservable command "Disable Force Monitoring"
            Disable the force monitoring.

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        if not self.system.state.is_operational():
            raise SystemNotOperationalError(self.__fully_qualified_command_id('DisableForceMonitoring'))

        self.pump.enable_force_monitoring(False)

        return ForceMonitoringService_pb2.DisableForceMonitoring_Responses()


    def SetForceLimit(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.SetForceLimit_Responses:
        """
        Executes the unobservable command "Set Force Limit"
            Set a custom limit.

        :param request: gRPC request containing the parameters passed:
            request.ForceLimit (Force Limit): The force limit to set. If higher than MaxDeviceForce, MaxDeviceForce will be used instead.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        if not self.system.state.is_operational():
            raise SystemNotOperationalError(self.__fully_qualified_command_id('SetForceLimit'))

        requested_force_limit = request.ForceLimit.Force.value
        self.pump.write_force_limit(requested_force_limit)

        return ForceMonitoringService_pb2.SetForceLimit_Responses()


    def Subscribe_ForceSensorValue(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.Subscribe_ForceSensorValue_Responses:
        """
        Requests the observable property Force Sensor Value
            The currently measured force as read by the force sensor.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            request.ForceSensorValue (Force Sensor Value): The currently measured force as read by the force sensor.
        """
        new_force_value = self.pump.read_force_sensor()
        force_value = new_force_value + 1 # force sending the first value
        while context.is_active():
            if self.system.state.is_operational():
                new_force_value = self.pump.read_force_sensor()
            # consider a value different from the one before if they differ in
            # the first 3 decimal places to reduce the load of value updates
            if not math.isclose(new_force_value, force_value, rel_tol=1.0e-3):
                force_value = new_force_value
                yield ForceMonitoringService_pb2.Subscribe_ForceSensorValue_Responses(
                    ForceSensorValue=ForceMonitoringService_pb2.DataType_Force(
                        Force=silaFW_pb2.Real(value=force_value)
                    )
                )
            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.1)


    def Subscribe_ForceLimit(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.Subscribe_ForceLimit_Responses:
        """
        Requests the observable property Force Limit
            The current force limit.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            request.ForceLimit (Force Limit): The current force limit.
        """
        new_force_limit = self.pump.get_force_limit()
        force_limit = new_force_limit + 1 # force sending the first value
        while context.is_active():
            if self.system.state.is_operational():
                new_force_limit = self.pump.get_force_limit()
            if not math.isclose(new_force_limit, force_limit):
                force_limit = new_force_limit
                yield ForceMonitoringService_pb2.Subscribe_ForceLimit_Responses(
                    ForceLimit=ForceMonitoringService_pb2.DataType_Force(
                        Force=silaFW_pb2.Real(value=force_limit)
                    )
                )
            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.1)


    def Subscribe_MaxDeviceForce(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.Subscribe_MaxDeviceForce_Responses:
        """
        Requests the observable property Maximum Device Force
            The maximum device force (i.e. the maximum force the pump hardware can take in continuous operation).

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            request.MaxDeviceForce (Maximum Device Force): The maximum device force (i.e. the maximum force the pump hardware can take in continuous operation).
        """
        new_max_device_force = self.pump.get_max_device_force()
        max_device_force = new_max_device_force + 1 # force sending the first value
        while context.is_active():
            if self.system.state.is_operational():
                new_max_device_force = self.pump.get_max_device_force()
            if not math.isclose(new_max_device_force, max_device_force):
                max_device_force = new_max_device_force
                yield ForceMonitoringService_pb2.Subscribe_MaxDeviceForce_Responses(
                    MaxDeviceForce=ForceMonitoringService_pb2.DataType_Force(
                        Force=silaFW_pb2.Real(value=max_device_force)
                    )
                )
            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.1)


    def Subscribe_ForceMonitoringEnabled(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.Subscribe_ForceMonitoringEnabled_Responses:
        """
        Requests the observable property Force Monitoring Enabled
            Whether force monitoring is enabled.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            request.ForceMonitoringEnabled (Force Monitoring Enabled): Whether force monitoring is enabled.
        """
        new_is_enabled = self.pump.is_force_monitoring_enabled()
        is_enabled = not new_is_enabled # force sending the first value
        while context.is_active():
            if self.system.state.is_operational():
                new_is_enabled = self.pump.is_force_monitoring_enabled()
            if new_is_enabled != is_enabled:
                is_enabled = new_is_enabled
                yield ForceMonitoringService_pb2.Subscribe_ForceMonitoringEnabled_Responses(
                    ForceMonitoringEnabled=silaFW_pb2.Boolean(value=is_enabled)
                )
            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.1)


    def Subscribe_ForceSafetyStopActive(self, request, context: grpc.ServicerContext) \
            -> ForceMonitoringService_pb2.Subscribe_ForceSafetyStopActive_Responses:
        """
        Requests the observable property Force Safety Stop Active
            Whether force safety stop is active.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            request.ForceSafetyStopActive (Force Safety Stop Active): Whether force safety stop is active.
        """
        new_safety_stop_active = self.pump.is_force_safety_stop_active()
        safety_stop_active = not new_safety_stop_active # force sending the first value
        while context.is_active():
            if self.system.state.is_operational():
                new_safety_stop_active = self.pump.is_force_safety_stop_active()
            if new_safety_stop_active != safety_stop_active:
                safety_stop_active = new_safety_stop_active
                yield ForceMonitoringService_pb2.Subscribe_ForceSafetyStopActive_Responses(
                    ForceSafetyStopActive=silaFW_pb2.Boolean(value=safety_stop_active)
                )
            # we add a small delay to give the client a chance to keep up.
            time.sleep(0.1)

