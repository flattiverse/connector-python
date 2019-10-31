#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-14
#

from enum import Enum


class UniverseStatus(Enum):
    Online = 0
    Offline = 1
    Maintenance = 2
