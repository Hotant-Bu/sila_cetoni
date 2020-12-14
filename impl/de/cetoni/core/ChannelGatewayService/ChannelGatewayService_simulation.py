"""
________________________________________________________________________

:PROJECT: SiLA2_python

*I/O Channel Gateway Service*

:details: ChannelGatewayService:
    This feature provides gateway functionality for the other I/O Features.

:file:    ChannelGatewayService_simulation.py
:authors: Florian Meinicke

:date: (creation)          2020-12-10T10:35:04.931355
:date: (last modification) 2020-12-10T10:35:04.931355

.. note:: Code generated by sila2codegenerator 0.2.0

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

# import SiLA2 library
import sila2lib.framework.SiLAFramework_pb2 as silaFW_pb2

# import gRPC modules for this feature
from .gRPC import ChannelGatewayService_pb2 as ChannelGatewayService_pb2
# from .gRPC import ChannelGatewayService_pb2_grpc as ChannelGatewayService_pb2_grpc

# import default arguments
from .ChannelGatewayService_default_arguments import default_dict


# noinspection PyPep8Naming,PyUnusedLocal
class ChannelGatewayServiceSimulation:
    """
    Implementation of the *I/O Channel Gateway Service* in *Simulation* mode
        The SiLA 2 driver for Qmix I/O Devices
    """

    def __init__(self):
        """Class initialiser"""

        logging.debug('Started server in mode: {mode}'.format(mode='Simulation'))

    def _get_command_state(self, command_uuid: str) -> silaFW_pb2.ExecutionInfo:
        """
        Method to fill an ExecutionInfo message from the SiLA server for observable commands

        :param command_uuid: The uuid of the command for which to return the current state

        :return: An execution info object with the current command state
        """

        #: Enumeration of silaFW_pb2.ExecutionInfo.CommandStatus
        command_status = silaFW_pb2.ExecutionInfo.CommandStatus.waiting
        #: Real silaFW_pb2.Real(0...1)
        command_progress = None
        #: Duration silaFW_pb2.Duration(seconds=<seconds>, nanos=<nanos>)
        command_estimated_remaining = None
        #: Duration silaFW_pb2.Duration(seconds=<seconds>, nanos=<nanos>)
        command_lifetime_of_execution = None

        # TODO: check the state of the command with the given uuid and return the correct information

        # just return a default in this example
        return silaFW_pb2.ExecutionInfo(
            commandStatus=command_status,
            progressInfo=(
                command_progress if command_progress is not None else None
            ),
            estimatedRemainingTime=(
                command_estimated_remaining if command_estimated_remaining is not None else None
            ),
            updatedLifetimeOfExecution=(
                command_lifetime_of_execution if command_lifetime_of_execution is not None else None
            )
        )

    def get_channel(self, metadata):
        """
        Get the channel that is identified by the channel name given in `metadata`

        :param metdata: The metadata of the call. It should contain the requested channel name
        :return: A valid channel object if the channel can be identified, otherwise a SiLAFrameworkError will be raised
        """
        return None

    def GetChannelIdentifiers(self, request, context: grpc.ServicerContext) \
            -> ChannelGatewayService_pb2.GetChannelIdentifiers_Responses:
        """
        Executes the unobservable command "Get Channel Identifiers"
            Get all possible channel names (identifiers) that the given Feature can use.

        :param request: gRPC request containing the parameters passed:
            request.FeatureIdentifier (Feature Identifier): A Fully Qualified Feature Identifier.
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: The return object defined for the command with the following fields:
            ChannelIdentifiers (Channel Identifiers): A list of channel names (identifiers) that the given Feature can use.
        """

        # initialise the return value
        return_value = None

        # TODO:
        #   Add implementation of Simulation for command GetChannelIdentifiers here and write the resulting response
        #   in return_value

        # fallback to default
        if return_value is None:
            return_value = ChannelGatewayService_pb2.GetChannelIdentifiers_Responses(
                **default_dict['GetChannelIdentifiers_Responses']
            )

        return return_value




    def Get_FCPAffectedByMetadata_ChannelIdentifier(self, request, context: grpc.ServicerContext) \
            -> ChannelGatewayService_pb2.Get_FCPAffectedByMetadata_ChannelIdentifier_Responses:
        """
        Requests the unobservable property FCPAffectedByMetadata Channel Identifier
            Specifies which Features/Commands/Properties of the SiLA server are affected by the Channel Identifier Metadata.

        :param request: An empty gRPC request object (properties have no parameters)
        :param context: gRPC :class:`~grpc.ServicerContext` object providing gRPC-specific information

        :returns: A response object with the following fields:
            AffectedCalls (AffectedCalls): A string containing a list of Fully Qualified Identifiers of Features, Commands and Properties for which the SiLA Client Metadata is expected as part of the respective RPCs.
        """

        # initialise the return value
        return_value: ChannelGatewayService_pb2.Get_FCPAffectedByMetadata_ChannelIdentifier_Responses = None

        # TODO:
        #   Add implementation of Simulation for property FCPAffectedByMetadata_ChannelIdentifier here and write the resulting response
        #   in return_value

        # fallback to default
        if return_value is None:
            return_value = ChannelGatewayService_pb2.Get_FCPAffectedByMetadata_ChannelIdentifier_Responses(
                **default_dict['Get_FCPAffectedByMetadata_ChannelIdentifier_Responses']
            )

        return return_value
