# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import DigitalOutChannelController_pb2 as DigitalOutChannelController__pb2


class DigitalOutChannelControllerStub(object):
    """Feature: Digital Out Channel Controller
    Allows to control one digital output channel of an I/O module
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetOutput = channel.unary_unary(
                '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/SetOutput',
                request_serializer=DigitalOutChannelController__pb2.SetOutput_Parameters.SerializeToString,
                response_deserializer=DigitalOutChannelController__pb2.SetOutput_Responses.FromString,
                )
        self.Get_NumberOfChannels = channel.unary_unary(
                '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Get_NumberOfChannels',
                request_serializer=DigitalOutChannelController__pb2.Get_NumberOfChannels_Parameters.SerializeToString,
                response_deserializer=DigitalOutChannelController__pb2.Get_NumberOfChannels_Responses.FromString,
                )
        self.Subscribe_State = channel.unary_stream(
                '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Subscribe_State',
                request_serializer=DigitalOutChannelController__pb2.Subscribe_State_Parameters.SerializeToString,
                response_deserializer=DigitalOutChannelController__pb2.Subscribe_State_Responses.FromString,
                )
        self.Get_FCPAffectedByMetadata_ChannelIndex = channel.unary_unary(
                '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Get_FCPAffectedByMetadata_ChannelIndex',
                request_serializer=DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Parameters.SerializeToString,
                response_deserializer=DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Responses.FromString,
                )


class DigitalOutChannelControllerServicer(object):
    """Feature: Digital Out Channel Controller
    Allows to control one digital output channel of an I/O module
    """

    def SetOutput(self, request, context):
        """Set Output
        Switch a digital output channel on or off.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get_NumberOfChannels(self, request, context):
        """Number Of Channels
        The number of digital output channels. This value is 0-indexed, i.e. the first channel has index 0, the second one index
        1 and so on.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe_State(self, request, context):
        """State
        The state of the channel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get_FCPAffectedByMetadata_ChannelIndex(self, request, context):
        """Channel Index
        The index of the channel that should be used.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DigitalOutChannelControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetOutput': grpc.unary_unary_rpc_method_handler(
                    servicer.SetOutput,
                    request_deserializer=DigitalOutChannelController__pb2.SetOutput_Parameters.FromString,
                    response_serializer=DigitalOutChannelController__pb2.SetOutput_Responses.SerializeToString,
            ),
            'Get_NumberOfChannels': grpc.unary_unary_rpc_method_handler(
                    servicer.Get_NumberOfChannels,
                    request_deserializer=DigitalOutChannelController__pb2.Get_NumberOfChannels_Parameters.FromString,
                    response_serializer=DigitalOutChannelController__pb2.Get_NumberOfChannels_Responses.SerializeToString,
            ),
            'Subscribe_State': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe_State,
                    request_deserializer=DigitalOutChannelController__pb2.Subscribe_State_Parameters.FromString,
                    response_serializer=DigitalOutChannelController__pb2.Subscribe_State_Responses.SerializeToString,
            ),
            'Get_FCPAffectedByMetadata_ChannelIndex': grpc.unary_unary_rpc_method_handler(
                    servicer.Get_FCPAffectedByMetadata_ChannelIndex,
                    request_deserializer=DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Parameters.FromString,
                    response_serializer=DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Responses.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DigitalOutChannelController(object):
    """Feature: Digital Out Channel Controller
    Allows to control one digital output channel of an I/O module
    """

    @staticmethod
    def SetOutput(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/SetOutput',
            DigitalOutChannelController__pb2.SetOutput_Parameters.SerializeToString,
            DigitalOutChannelController__pb2.SetOutput_Responses.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get_NumberOfChannels(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Get_NumberOfChannels',
            DigitalOutChannelController__pb2.Get_NumberOfChannels_Parameters.SerializeToString,
            DigitalOutChannelController__pb2.Get_NumberOfChannels_Responses.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe_State(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Subscribe_State',
            DigitalOutChannelController__pb2.Subscribe_State_Parameters.SerializeToString,
            DigitalOutChannelController__pb2.Subscribe_State_Responses.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get_FCPAffectedByMetadata_ChannelIndex(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sila2.de.cetoni.io.digitaloutchannelcontroller.v1.DigitalOutChannelController/Get_FCPAffectedByMetadata_ChannelIndex',
            DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Parameters.SerializeToString,
            DigitalOutChannelController__pb2.Get_FCPAffectedByMetadata_ChannelIndex_Responses.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
