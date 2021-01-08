"""
________________________________________________________________________

:PROJECT: SiLA2_python

*Continuous Flow Configuration Service*

:details: ContinuousFlowConfigurationService:
    Allows to configure the parameters of a continuous flow pump.

:file:    ContinuousFlowConfigurationService_servicer.py
:authors: Florian Meinicke

:date: (creation)          2020-10-22T07:15:47.982414
:date: (last modification) 2020-10-22T07:15:47.982414

.. note:: Code generated by sila2codegenerator 0.3.2.dev

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
import grpc

# meta packages
from typing import Union

# import SiLA2 library
import sila2lib.framework.SiLAFramework_pb2 as silaFW_pb2
from sila2lib.error_handling.server_err import SiLAError

# import gRPC modules for this feature
from .gRPC import ContinuousFlowConfigurationService_pb2 as ContinuousFlowConfigurationService_pb2
from .gRPC import ContinuousFlowConfigurationService_pb2_grpc as ContinuousFlowConfigurationService_pb2_grpc

# import simulation and real implementation
from .ContinuousFlowConfigurationService_simulation import ContinuousFlowConfigurationServiceSimulation
from .ContinuousFlowConfigurationService_real import ContinuousFlowConfigurationServiceReal

# import SiLA errors
from impl.common.qmix_errors import SiLAValidationError, QmixSDKSiLAError, DeviceError

# import qmixsdk
from qmixsdk import qmixpump

class ContinuousFlowConfigurationService(ContinuousFlowConfigurationService_pb2_grpc.ContinuousFlowConfigurationServiceServicer):
    """
    Allows to control a continuous flow pumps that is made up of two syringe pumps
    """
    implementation: Union[ContinuousFlowConfigurationServiceSimulation, ContinuousFlowConfigurationServiceReal]
    simulation_mode: bool

    def __init__(self, pump: qmixpump.ContiFlowPump, sila2_conf, simulation_mode: bool = True):
        """
        Class initialiser.

        :param pump: A valid `qxmixpump.ContiFlowPump` for this service to use
        :param sila2_conf: The config of the server
        :param simulation_mode: Sets whether at initialisation the simulation mode is active or the real mode.
        """

        self.pump = pump
        self.sila2_conf = sila2_conf

        self.simulation_mode = simulation_mode
        if simulation_mode:
            self.switch_to_simulation_mode()
        else:
            self.switch_to_real_mode()

    def _inject_implementation(self,
                               implementation: Union[ContinuousFlowConfigurationServiceSimulation,
                                                     ContinuousFlowConfigurationServiceReal]
                               ) -> bool:
        """
        Dependency injection of the implementation used.
            Allows to set the class used for simulation/real mode.

        :param implementation: A valid implementation of the ContiflowServicer.
        """

        self.implementation = implementation
        return True

    def switch_to_simulation_mode(self):
        """Method that will automatically be called by the server when the simulation mode is requested."""
        self.simulation_mode = True
        self._inject_implementation(ContinuousFlowConfigurationServiceSimulation())

    def switch_to_real_mode(self):
        """Method that will automatically be called by the server when the real mode is requested."""
        self.simulation_mode = False
        self._inject_implementation(
            ContinuousFlowConfigurationServiceReal(self.pump, self.sila2_conf))

    def SetSwitchingMode(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.SetSwitchingMode_Responses:
        """
        Executes the unobservable command "Set Switching Mode"
            Sets the switching mode for syringe pump switchover if one syringe pump runs empty.

        :param request: gRPC request containing the parameters passed:
            request.SwitchingMode (Switching Mode): The new switching mode to set
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "SetSwitchingMode called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        try:
            return self.implementation.SetSwitchingMode(request, context)
        except (SiLAValidationError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context)
            return None

    def SetRefillFlowRate(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.SetRefillFlowRate_Responses:
        """
        Executes the unobservable command "Set Refill Flow Rate"
            Set the refill flow rate for the continuous flow pump. The refill flow speed limits the maximum flow that is possible with a contiflow pump.

        :param request: gRPC request containing the parameters passed:
            request.RefillFlowRate (Refill Flow Rate): The refill flow rate to set
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "SetRefillFlowRate called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        try:
            return self.implementation.SetRefillFlowRate(request, context)
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def SetCrossFlowDuration(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.SetCrossFlowDuration_Responses:
        """
        Executes the unobservable command "Set Cross Flow Duration"
            Set the cross flow duration for the continuous flow pump. The cross flow duration is the time the pump running empty decelerates while the filled pump accelerates.

        :param request: gRPC request containing the parameters passed:
            request.CrossFlowDuration (Cross Flow Duration): The cross flow duration to set
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "SetCrossFlowDuration called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        try:
            return self.implementation.SetCrossFlowDuration(request, context)
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def SetOverlapDuration(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.SetOverlapDuration_Responses:
        """
        Executes the unobservable command "Set Overlap Duration"
            Set the overlap duration for the continuous flow pump. The overlap duration is a time the refilled pump will start earlier than the empty pump stops. You can use this time to ensure that the system is already pressurized when switching over.

        :param request: gRPC request containing the parameters passed:
            request.OverlapDuration (Overlap Duration): The overlap duration to set
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            request.EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "SetOverlapDuration called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        try:
            return self.implementation.SetOverlapDuration(request, context)
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Subscribe_SwitchingMode(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_SwitchingMode_Responses:
        """
        Requests the observable property Switching Mode
            Get the switching mode for syringe pump switchover if one syringe pump runs empty.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.SwitchingMode (Switching Mode): Get the switching mode for syringe pump switchover if one syringe pump runs empty.
        """

        logging.debug(
            "Property SwitchingMode requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_SwitchingMode(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Subscribe_MaxRefillFlowRate(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_MaxRefillFlowRate_Responses:
        """
        Requests the observable property Max Refill Flow Rate
            Get the maximum possible refill flow rate for the continuous flow pump.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.MaxRefillFlowRate (Max Refill Flow Rate): Get the maximum possible refill flow rate for the continuous flow pump.
        """

        logging.debug(
            "Property MaxRefillFlowRate requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_MaxRefillFlowRate(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Subscribe_RefillFlowRate(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_RefillFlowRate_Responses:
        """
        Requests the observable property Refill Flow Rate
            Get the refill flow rate for the continuous flow pump.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.RefillFlowRate (Refill Flow Rate): Get the refill flow rate for the continuous flow pump.
        """

        logging.debug(
            "Property RefillFlowRate requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_RefillFlowRate(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Subscribe_MinFlowRate(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_MinFlowRate_Responses:
        """
        Requests the observable property Min Flow Rate
            Get the minimum flow rate that is theoretically possible with the continuous flow pump.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.MinFlowRate (Min Flow Rate): Get the minimum flow rate that is theoretically possible with the continuous flow pump.
        """

        logging.debug(
            "Property MinFlowRate requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_MinFlowRate(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Subscribe_CrossFlowDuration(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_CrossFlowDuration_Responses:
        """
        Requests the observable property Cross Flow Duration
            Get the cross flow duration for the continuous flow pump.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.CrossFlowDuration (Cross Flow Duration): Get the cross flow duration for the continuous flow pump.
        """

        logging.debug(
            "Property CrossFlowDuration requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_CrossFlowDuration(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Subscribe_OverlapDuration(self, request, context: grpc.ServicerContext) \
            -> ContinuousFlowConfigurationService_pb2.Subscribe_OverlapDuration_Responses:
        """
        Requests the observable property Overlap Duration
            Get the overlap duration for the continuous flow pump.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            request.OverlapDuration (Overlap Duration): Get the overlap duration for the continuous flow pump.
        """

        logging.debug(
            "Property OverlapDuration requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_OverlapDuration(request, context):
                yield value
        except DeviceError as err:
            err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

