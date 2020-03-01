#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-15
#


from enum import Enum


class Privileges(Enum):
    Nothing = 0
    Join = 1
    Manage_Units = 2
    Manage_Regions = 4
    Manage_SYSTEMS = 8
    Manage_Universe = 16
