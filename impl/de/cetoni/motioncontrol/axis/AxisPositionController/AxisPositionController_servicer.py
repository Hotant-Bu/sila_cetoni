"""
________________________________________________________________________

:PROJECT: sila_cetoni

*Axis Position Controller*

:details: AxisPositionController:
    Allows to control the position of one axis of an axis system

:file:    AxisPositionController_servicer.py
:authors: Florian Meinicke

:date: (creation)          2020-12-17T10:31:32.029797
:date: (last modification) 2021-07-09T10:33:24.199806

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
import grpc

# meta packages
from typing import Union

# import SiLA2 library
import sila2lib.framework.SiLAFramework_pb2 as silaFW_pb2
from impl.common.errors import QmixSDKSiLAError, SiLAError, DeviceError

# import gRPC modules for this feature
from .gRPC import AxisPositionController_pb2 as AxisPositionController_pb2
from .gRPC import AxisPositionController_pb2_grpc as AxisPositionController_pb2_grpc

# import simulation and real implementation
from .AxisPositionController_simulation import AxisPositionControllerSimulation
from .AxisPositionController_real import AxisPositionControllerReal



class AxisPositionController(AxisPositionController_pb2_grpc.AxisPositionControllerServicer):
    """
    Allows to control motion systems like axis systems
    """
    implementation: Union[AxisPositionControllerSimulation, AxisPositionControllerReal]
    simulation_mode: bool

    def __init__(self, axis_system, simulation_mode: bool = True):
        """
        Class initialiser.

        :param axis_system: The axis system that this feature shall operate on
        :param simulation_mode: Sets whether at initialisation the simulation mode is active or the real mode.
        """

        self.axis_system = axis_system
        self.simulation_mode = simulation_mode
        if simulation_mode:
            self.switch_to_simulation_mode()
        else:
            self.switch_to_real_mode()

    def _inject_implementation(self,
                               implementation: Union[AxisPositionControllerSimulation,
                                                     AxisPositionControllerReal]
                               ) -> bool:
        """
        Dependency injection of the implementation used.
            Allows to set the class used for simulation/real mode.

        :param implementation: A valid implementation of the MotionControlServicer.
        """

        self.implementation = implementation
        return True

    def switch_to_simulation_mode(self):
        """Method that will automatically be called by the server when the simulation mode is requested."""
        self.simulation_mode = True
        self._inject_implementation(AxisPositionControllerSimulation())

    def switch_to_real_mode(self):
        """Method that will automatically be called by the server when the real mode is requested."""
        self.simulation_mode = False
        self._inject_implementation(AxisPositionControllerReal(self.axis_system))

    def MoveToPosition(self, request, context: grpc.ServicerContext) \
            -> silaFW_pb2.CommandConfirmation:
        """
        Executes the observable command "Move To Position"
            Move the axis to the given position with a certain velocity

        :param request: gRPC request containing the parameters passed:
            request.Position (Position): The position to move to. Has to be in the range between MinimumPosition and MaximumPosition. See PositionUnit for the unit that is used for a specific axis. E.g. for rotational axis systems one of the axes needs a position specified in radians.
            request.Velocity (Velocity): The velocity value for the movement. Has to be in the range between MinimumVelocity and MaximumVelocity.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A command confirmation object with the following information:
            commandId: A command id with which this observable command can be referenced in future calls
            lifetimeOfExecution: The (maximum) lifetime of this command call.
        """

        logging.debug(
            "MoveToPosition called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        # parameter validation
        # if request.my_paramameter.value out of scope :
        #        sila_val_err = SiLAValidationError(parameter="myParameter",
        #                                           msg=f"Parameter {request.my_parameter.value} out of scope!")
        #        sila_val_err.raise_rpc_error(context)

        try:
            return self.implementation.MoveToPosition(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def MoveToPosition_Info(self, request, context: grpc.ServicerContext) \
            -> silaFW_pb2.ExecutionInfo:
        """
        Returns execution information regarding the command call :meth:`~.MoveToPosition`.

        :param request: A request object with the following properties
            CommandExecutionUUID: The UUID of the command executed.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: An ExecutionInfo response stream for the command with the following fields:
            commandStatus: Status of the command (enumeration)
            progressInfo: Information on the progress of the command (0 to 1)
            estimatedRemainingTime: Estimate of the remaining time required to run the command
            updatedLifetimeOfExecution: An update on the execution lifetime
        """

        logging.debug(
            "MoveToPosition_Info called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.MoveToPosition_Info(request, context):
                yield value
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def MoveToPosition_Result(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.MoveToPosition_Responses:
        """
        Returns the final result of the command call :meth:`~.MoveToPosition`.

        :param request: A request object with the following properties
            CommandExecutionUUID: The UUID of the command executed.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "MoveToPosition_Result called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.MoveToPosition_Result(request, context)
        except SiLAError as err:
            err.raise_rpc_error(context=context)


    def MoveToHomePosition(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.MoveToHomePosition_Responses:
        """
        Executes the unobservable command "Move To Home Position"
            Move the axis to its home position

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "MoveToHomePosition called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        # parameter validation
        # if request.my_paramameter.value out of scope :
        #        sila_val_err = SiLAValidationError(parameter="myParameter",
        #                                           msg=f"Parameter {request.my_parameter.value} out of scope!")
        #        sila_val_err.raise_rpc_error(context)

        try:
            return self.implementation.MoveToHomePosition(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def StopMoving(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.StopMoving_Responses:
        """
        Executes the unobservable command "Stop Moving"
            Immediately stops axis movement of a single axis

        :param request: gRPC request containing the parameters passed:
            request.EmptyParameter (Empty Parameter): An empty parameter data type used if no parameter is required.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            EmptyResponse (Empty Response): An empty response data type used if no response is required.
        """

        logging.debug(
            "StopMoving called in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )

        # parameter validation
        # if request.my_paramameter.value out of scope :
        #        sila_val_err = SiLAValidationError(parameter="myParameter",
        #                                           msg=f"Parameter {request.my_parameter.value} out of scope!")
        #        sila_val_err.raise_rpc_error(context)

        try:
            return self.implementation.StopMoving(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Subscribe_Position(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Subscribe_Position_Responses:
        """
        Requests the observable property Position
            The current position of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response stream with the following fields:
            Position (Position): The current position of an axis
        """

        logging.debug(
            "Property Position requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            for value in self.implementation.Subscribe_Position(request, context):
                yield value
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)


    def Get_PositionUnit(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_PositionUnit_Responses:
        """
        Requests the unobservable property PositionUnit
            The position unit used for specifying the position of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            PositionUnit (PositionUnit): The position unit used for specifying the position of an axis
        """

        logging.debug(
            "Property PositionUnit requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_PositionUnit(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Get_MinimumPosition(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_MinimumPosition_Responses:
        """
        Requests the unobservable property Minimum Position
            The minimum position limit of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            MinimumPosition (Minimum Position): The minimum position limit of an axis
        """

        logging.debug(
            "Property MinimumPosition requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_MinimumPosition(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Get_MaximumPosition(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_MaximumPosition_Responses:
        """
        Requests the unobservable property Maximum Position
            The maximum position limit of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            MaximumPosition (Maximum Position): The maximum position limit of an axis
        """

        logging.debug(
            "Property MaximumPosition requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_MaximumPosition(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Get_MinimumVelocity(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_MinimumVelocity_Responses:
        """
        Requests the unobservable property Minimum Velocity
            The minimum velocity limit of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            MinimumVelocity (Minimum Velocity): The minimum velocity limit of an axis
        """

        logging.debug(
            "Property MinimumVelocity requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_MinimumVelocity(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Get_MaximumVelocity(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_MaximumVelocity_Responses:
        """
        Requests the unobservable property Maximum Velocity
            The maximum velocity limit of an axis

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            MaximumVelocity (Maximum Velocity): The maximum velocity limit of an axis
        """

        logging.debug(
            "Property MaximumVelocity requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_MaximumVelocity(request, context)
        except (SiLAError, DeviceError) as err:
            if isinstance(err, DeviceError):
                err = QmixSDKSiLAError(err)
            err.raise_rpc_error(context=context)

    def Get_FCPAffectedByMetadata_AxisIdentifier(self, request, context: grpc.ServicerContext) \
            -> AxisPositionController_pb2.Get_FCPAffectedByMetadata_AxisIdentifier_Responses:
        """
        Requests the unobservable property FCPAffectedByMetadata Axis Identifier
            Specifies which Features/Commands/Properties of the SiLA server are affected by the Axis Identifier Metadata.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            AffectedCalls (AffectedCalls): A string containing a list of Fully Qualified Identifiers of Features, Commands and Properties for which the SiLA Client Metadata is expected as part of the respective RPCs.
        """

        logging.debug(
            "Property FCPAffectedByMetadata_AxisIdentifier requested in {current_mode} mode".format(
                current_mode=('simulation' if self.simulation_mode else 'real')
            )
        )
        try:
            return self.implementation.Get_FCPAffectedByMetadata_AxisIdentifier(request, context)
        except SiLAError as err:
            err.raise_rpc_error(context=context)
