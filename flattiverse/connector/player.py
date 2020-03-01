#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2020-03-01
#

from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class Player:
    def __init__(self, packet):
        self.id = packet.base_address
        self.account = packet.id
        reader: BinaryMemoryReader = packet.reader
        self.name = reader.read_string_non_null()
        self.online = reader.read_boolean()
        self.single = reader.read_single()
        self.ping = self.single
        print("Player", self.name, "read")
