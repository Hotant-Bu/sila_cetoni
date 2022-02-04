from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.client import SilaClient

if TYPE_CHECKING:

    from .batteryprovider import BatteryProviderClient


class Client(SilaClient):

    BatteryProvider: BatteryProviderClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)