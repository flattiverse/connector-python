#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2020-03-01
#
from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class Galaxy:

    def __init__(self, universe, packet):
        self.universe = universe
        self.id = packet.sub_address

        reader: BinaryMemoryReader = packet.reader
        self.name = reader.read_string_non_null()
        self.spawn = reader.read_boolean()

    def update_from_packet(self, packet):
        reader: BinaryMemoryReader = packet.reader
        self.name = reader.read_string_non_null()
        self.spawn = reader.read_boolean()
