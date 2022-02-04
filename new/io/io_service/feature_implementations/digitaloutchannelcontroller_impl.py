from __future__ import annotations
import logging
from queue import Queue

import time
from concurrent.futures import Executor
from threading import Event
from typing import Any, Dict, List, Optional, Union

from sila2.framework import Command, Feature, FullyQualifiedIdentifier, Property

from application.system import ApplicationSystem
from qmixsdk.qmixdigio import DigitalOutChannel

from ..generated.digitaloutchannelcontroller import (
    DigitalOutChannelControllerBase,
    DigitalOutChannelControllerFeature,
    SetOutput_Responses,
    State,
    InvalidChannelIndex,
)


class DigitalOutChannelControllerImpl(DigitalOutChannelControllerBase):
    __system: ApplicationSystem
    __channels: List[DigitalOutChannel]
    __channel_index_identifier: FullyQualifiedIdentifier
    __state_queues: List[Queue[State]]  # same number of items and order as `__channels`
    __stop_event: Event

    def __init__(self, channels: List[DigitalOutChannel], executor: Executor):
        super().__init__()
        self.__system = ApplicationSystem()
        self.__channels = channels
        self.__channel_index_identifier = DigitalOutChannelControllerFeature["ChannelIndex"].fully_qualified_identifier
        self.__stop_event = Event()

        self.__state_queues = []
        for i in range(len(self.__channels)):
            self.__state_queues += [Queue()]
            self.update_State(
                "On" if self.__channels[i].is_output_on() else "Off",
                queue=self.__state_queues[i],
            )
            executor.submit(self.__make_state_updater(i), self.__stop_event)

    def __make_state_updater(self, i: int):
        def update_state(stop_event: Event):
            new_is_on = is_on = self.__channels[i].is_output_on()
            while not stop_event.is_set():
                if self.__system.state.is_operational():
                    new_is_on = self.__channels[i].is_output_on()
                if new_is_on != is_on:
                    is_on = new_is_on
                    self.update_State("On" if is_on else "Off", queue=self.__state_queues[i])
                time.sleep(0.1)

        return update_state

    def get_NumberOfChannels(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> int:
        return len(self.__channels)

    def State_on_subscription(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> Optional[Queue[State]]:
        channel_index: int = metadata.pop(self.__channel_index_identifier)
        try:
            return self.__state_queues[channel_index]
        except IndexError:
            raise InvalidChannelIndex(
                message=f"The sent channel index {channel_index} is invalid. The index must be between 0 and {len(self.__channels) - 1}.",
            )

    def SetOutput(self, State: State, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> SetOutput_Responses:
        channel_index: int = metadata.pop(self.__channel_index_identifier)
        logging.debug(f"channel id: {channel_index}")
        try:
            self.__channels[channel_index].write_on(State == "On")
        except IndexError:
            raise InvalidChannelIndex(
                message=f"The sent channel index {channel_index} is invalid. The index must be between 0 and {len(self.__channels) - 1}.",
            )

    def get_calls_affected_by_ChannelIndex(
        self,
    ) -> List[Union[Feature, Command, Property, FullyQualifiedIdentifier]]:
        return [
            DigitalOutChannelControllerFeature["State"],
            DigitalOutChannelControllerFeature["SetOutput"],
        ]

    def stop(self) -> None:
        self.__stop_event.set()
