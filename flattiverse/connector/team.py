#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-15
#
from flattiverse.connector.packet import Packet
from flattiverse.connector.universe import Universe
from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class Team:

    def __init__(self, universe: Universe, packet: Packet) -> None:
        self.universe = universe
        self.id = packet.sub_address

        self.name = ""
        self.r = 0.0
        self.g = 0.0
        self.b = 0.0

        self.update_from_packet(packet)

    def update_from_packet(self, packet):
        reader: BinaryMemoryReader = packet.reader
        self.name = reader.read_string()
        self.r = reader.read_byte() / 255
        self.g = reader.read_byte() / 255
        self.b = reader.read_byte() / 255

    def console_color(self):
        r = 0 if self.r < 0.5 else 1
        g = 0 if self.g < 0.5 else 2
        b = 0 if self.b < 0.5 else 4
        return r+g+b
