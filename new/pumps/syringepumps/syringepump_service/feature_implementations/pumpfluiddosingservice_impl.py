from __future__ import annotations
import datetime
import importlib

import re
import logging
import time, math
from threading import Event
from concurrent.futures import Executor

from typing import Any, Dict, Union

from sila2.framework import FullyQualifiedIdentifier, Command, Property
from sila2.server import ObservableCommandInstance
from sila2.framework.command.execution_info import CommandExecutionStatus
from sila2.framework.errors.validation_error import ValidationError
from sila2.framework.errors.undefined_execution_error import UndefinedExecutionError

from application.system import ApplicationSystem
from qmixsdk.qmixbus import PollingTimer
from qmixsdk.qmixpump import Pump

from ....validate import validate

from ..generated.pumpfluiddosingservice import (
    DoseVolume_Responses,
    GenerateFlow_Responses,
    PumpFluidDosingServiceBase,
    PumpFluidDosingServiceFeature,
    SetFillLevel_Responses,
    StopDosage_Responses,
)


class SystemNotOperationalError(UndefinedExecutionError):
    def __init__(self, command_or_property: Union[Command, Property]):
        super().__init__(
            "Cannot {} {} because the system is not in an operational state.".format(
                "execute" if isinstance(command_or_property, Command) else "read from",
                command_or_property.fully_qualified_identifier,
            )
        )


# TODO
def requires_operational_system(func):
    def wrapper(self, *, metadata):
        print(func.__name__)
        print(func.__class__)
        print(func.__module__)
        print(func.__qualname__)
        regex = re.compile("(\w+)Impl\.(\w+)")
        feature, command = regex.search(func.__qualname__).group(1, 2)
        print(feature, command)
        # m = importlib.import_module(feature+"Feature")
        print(ApplicationSystem().state.is_operational())
        func(self, metadata=metadata)

    return wrapper

class PumpFluidDosingServiceImpl(PumpFluidDosingServiceBase):
    __pump: Pump
    __system: ApplicationSystem
    __stop_event: Event
    __force_flow_rate_update: bool = True
    __force_max_flow_rate_update: bool = True
    __force_fill_level_update: bool = True
    __force_max_fill_level_update: bool = True

    def __init__(self, pump: Pump, executor: Executor):
        super().__init__()
        self.__pump = pump
        self.__system = ApplicationSystem()
        self.__stop_event = Event()

        def update_flow_rate(stop_event: Event):
            while not stop_event.is_set():
                new_flow_rate = self.__pump.get_flow_is() if self.__system.state.is_operational() else 0
                if self.__force_flow_rate_update or not math.isclose(new_flow_rate, flow_rate):
                    flow_rate = new_flow_rate
                    self.update_FlowRate(flow_rate)
                    self.__force_flow_rate_update = False
                time.sleep(0.1)

        def update_max_flow_rate(stop_event: Event):
            while not stop_event.is_set():
                if self.__system.state.is_operational():
                    new_max_flow_rate = self.__pump.get_flow_rate_max()
                if self.__force_max_flow_rate_update or not math.isclose(new_max_flow_rate, max_flow_rate):
                    max_flow_rate = new_max_flow_rate
                    self.update_MaxFlowRate(max_flow_rate)
                    self.__force_max_flow_rate_update = False
                time.sleep(0.1)

        def update_fill_level(stop_event: Event):
            while not stop_event.is_set():
                if self.__system.state.is_operational():
                    new_fill_level = self.__pump.get_fill_level()
                if self.__force_fill_level_update or not math.isclose(new_fill_level, fill_level):
                    fill_level = new_fill_level
                    self.update_SyringeFillLevel(fill_level)
                    self.__force_fill_level_update = False
                time.sleep(0.1)

        def update_max_fill_level(stop_event: Event):
            while not stop_event.is_set():
                if self.__system.state.is_operational():
                    new_max_fill_level = self.__pump.get_volume_max()
                if self.__force_max_fill_level_update or not math.isclose(new_max_fill_level, max_fill_level):
                    max_fill_level = new_max_fill_level
                    self.update_MaxSyringeFillLevel(max_fill_level)
                    self.__force_max_fill_level_update = False
                time.sleep(0.1)

        executor.submit(update_flow_rate, self.__stop_event)
        executor.submit(update_max_flow_rate, self.__stop_event)
        executor.submit(update_fill_level, self.__stop_event)
        executor.submit(update_max_fill_level, self.__stop_event)

    def FlowRate_on_subscription(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> None:
        self.__force_flow_rate_update = True

    def MaxFlowRate_on_subscription(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> None:
        self.__force_max_flow_rate_update = True

    def SyringeFillLevel_on_subscription(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> None:
        self.__force_fill_level_update = True

    def MaxSyringeFillLevel_on_subscription(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> None:
        self.__force_max_fill_level_update = True

    @requires_operational_system
    def StopDosage(self, *, metadata: Dict[FullyQualifiedIdentifier, Any]) -> StopDosage_Responses:
        if not self.__system.state.is_operational():
            raise SystemNotOperationalError(PumpFluidDosingServiceFeature["StopDosage"])
        self.__pump.stop_pumping()

    def _wait_dosage_finished(self, instance: ObservableCommandInstance):
        """
        The function waits until the last dosage command has finished or
        until a timeout occurs. The timeout is estimated from the dosage's flow
        and target volume
        """

        if not self.__pump.is_pumping():
            instance.status = CommandExecutionStatus.finishedSuccessfully
            instance.progress = 1

        target_volume = self.__pump.get_target_volume()
        logging.debug("target volume: %f", target_volume)
        flow_in_sec = self.__pump.get_flow_is() / self.__pump.get_flow_unit().time_unitid.value
        if flow_in_sec == 0:
            # try again, maybe the pump didn't start pumping yet
            time.sleep(0.5)
            flow_in_sec = self.__pump.get_flow_is() / self.__pump.get_flow_unit().time_unitid.value
        if flow_in_sec == 0:
            instance.status = CommandExecutionStatus.finishedWithError
            instance.progress = 1
            logging.error("The pump didn't start pumping. Last error: %s", self.__pump.read_last_error())

        logging.debug("flow_in_sec: %f", flow_in_sec)
        dosing_time = datetime.timedelta(seconds=self.__pump.get_target_volume() / flow_in_sec + 2)  # +2 sec buffer
        logging.debug("dosing_time_s: %fs", dosing_time.seconds)
        # send first info immediately
        instance.status = CommandExecutionStatus.running
        instance.progress = 0
        instance.estimated_remaining_time = dosing_time

        timer = PollingTimer(period_ms=dosing_time.seconds * 1000)
        message_timer = PollingTimer(period_ms=500)
        is_pumping = True
        POLLING_TIMEOUT = datetime.timedelta(seconds=0.1)
        while is_pumping and not timer.is_expired():
            time.sleep(POLLING_TIMEOUT.seconds)
            dosing_time -= POLLING_TIMEOUT
            if message_timer.is_expired():
                logging.info("Fill level: %s", self.__pump.get_fill_level())
                instance.status = CommandExecutionStatus.running
                instance.progress = self.__pump.get_dosed_volume() / target_volume
                instance.estimated_remaining_time = dosing_time
                message_timer.restart()
            is_pumping = self.__pump.is_pumping()

        if not is_pumping and not self.__pump.is_in_fault_state() and self.__pump.is_enabled():
            instance.status = CommandExecutionStatus.finishedSuccessfully
            instance.progress = 1
            instance.estimated_remaining_time = datetime.timedelta(0)
        else:
            instance.status = CommandExecutionStatus.finishedWithError
            instance.progress = 1
            instance.estimated_remaining_time = datetime.timedelta(0)
            logging.error("An unexpected error occurred: %s", self.__pump.read_last_error())

    def SetFillLevel(
        self,
        FillLevel: float,
        FlowRate: float,
        *,
        metadata: Dict[FullyQualifiedIdentifier, Any],
        instance: ObservableCommandInstance
    ) -> SetFillLevel_Responses:
        if not self.__system.state.is_operational():
            raise SystemNotOperationalError(PumpFluidDosingServiceFeature["SetFillLevel"])

        validate(self.__pump, PumpFluidDosingServiceFeature["SetFillLevel"], FlowRate, 1, fill_level=FillLevel, fill_level_id=0)
        # self.__pump.stop_pumping() # only one dosage allowed
        # time.sleep(0.25) # wait for the currently running dosage to catch up

        self.__pump.set_fill_level(FillLevel, FlowRate)
        self._wait_dosage_finished(instance)

    def DoseVolume(
        self,
        Volume: float,
        FlowRate: float,
        *,
        metadata: Dict[FullyQualifiedIdentifier, Any],
        instance: ObservableCommandInstance
    ) -> DoseVolume_Responses:
        if not self.__system.state.is_operational():
            raise SystemNotOperationalError(PumpFluidDosingServiceFeature["DoseVolume"])

        validate(self.__pump, PumpFluidDosingServiceFeature["DoseVolume"], FlowRate, 1, volume=Volume, volume_id=0)
        # self.__pump.stop_pumping() # only one dosage allowed
        # time.sleep(0.25) # wait for the currently running dosage to catch up

        self.__pump.pump_volume(Volume, FlowRate)
        self._wait_dosage_finished(instance)

    def GenerateFlow(
        self, FlowRate: float, *, metadata: Dict[FullyQualifiedIdentifier, Any], instance: ObservableCommandInstance
    ) -> GenerateFlow_Responses:
        if not self.__system.state.is_operational():
            raise SystemNotOperationalError(PumpFluidDosingServiceFeature["GenerateFlow"])

        # `FlowRate` is negative to indicate aspiration of fluid.
        # Since `validate` tests against 0 and the max flow rate of
        # the pump, we pass the absolute value of the `FlowRate`.
        validate(self.__pump, PumpFluidDosingServiceFeature["GenerateFlow"], abs(FlowRate), 0)
        # self.__pump.stop_pumping() # only one dosage allowed
        # time.sleep(0.25) # wait for the currently running dosage to catch up

        self.__pump.generate_flow(FlowRate)
        self._wait_dosage_finished(instance)

    def stop(self) -> None:
        self.__stop_event.set()