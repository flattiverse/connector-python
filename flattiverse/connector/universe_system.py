#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2020-03-01
#
from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class UniverseSystem:
    def __init__(self, reader: BinaryMemoryReader):
        self.kind = reader.read_byte()
        self.start_level = reader.read_byte()
        self.end_level = reader.read_byte()

    @property
    def in_use(self):
        return self.start_level != 0 or self.end_level != 0
