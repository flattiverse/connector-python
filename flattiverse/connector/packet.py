#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-13
#


from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class Packet:
    HAS_COMMAND = 0b1000_0000
    HAS_SESSION = 0b0100_0000
    HAS_BASE_ADDRESS = 0b0000_1000
    HAS_SUB_ADDRESS = 0b0000_0100
    HAS_ID = 0b0000_0010
    HAS_HELPER = 0b0000_0001

    def __init__(self):
        self.is_out_of_band = False
        self.reader = None
        self.command = 0
        self.session = 0
        self.base_address = 0
        self.sub_address = 0
        self.id = 0
        self.helper = 0

    def parse(self, reader: BinaryMemoryReader):
        if reader.size <= 0:
            return False

        header = reader.read_byte()
        self.is_out_of_band = self.receive_header_is_out_of_band(header)
        payload_length = self.parse_payload_length(header, reader)
        if not self.is_out_of_band:
            self.fill_header_variables_from_received_data(header, reader)
        self.reader = reader.cut(payload_length)

        return True

    @staticmethod
    def receive_header_is_out_of_band(header):
        return header & 0b0011_0000 == 0b0011_0000

    @staticmethod
    def parse_payload_length(header, reader):
        payload_length_bits = (header & 0b0011_0000) >> 4

        if payload_length_bits == 0:
            return 0
        if payload_length_bits == 1:
            return reader.read_byte() + 1
        if payload_length_bits == 2:
            return reader.read_uint16() + 1
        if payload_length_bits == 3:
            return header & 0x0f

    def fill_header_variables_from_received_data(self, header, reader):
        self.command = reader.read_byte() if header & self.HAS_COMMAND else 0
        self.session = reader.read_byte() if header & self.HAS_SESSION else 0
        self.base_address = reader.read_uint16() if header & self.HAS_BASE_ADDRESS else 0
        self.sub_address = reader.read_byte() if header & self.HAS_SUB_ADDRESS else 0
        self.id = reader.read_uint32() if header & self.HAS_ID else 0
        self.helper = reader.read_byte() if header & self.HAS_HELPER else 0
