#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-14
#

from enum import Enum


class UniverseMode(Enum):
    Mission = 0
    STF = 1
    Domination = 2