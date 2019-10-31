#!/usr/bin/env python3
# Created at 2019-10-13 by Harald Melcher

import struct


class BinaryMemoryReader:
    def __init__(self, buffer, position):
        self.buffer = buffer
        self.position = position
        self.size = len(buffer) - position

    def require(self, byte_count):
        if byte_count > len(self.buffer):
            raise MemoryError("Not enough space for read operation")

    def read_byte(self):
        self.require(1)
        self.position += 1
        self.size -= 1
        return self.buffer[self.position - 1]

    def read_uint(self, length):
        result = 0
        for pos in range(length):
            result = result | (self.read_byte() << 8 * pos)
        return result

    def read_uint16(self):
        return self.read_uint(2)

    def read_uint32(self):
        return self.read_uint(4)

    def read_single(self):
        if self.size < 4:
            raise MemoryError("To little data for float")
        single = struct.unpack_from('<f', self.buffer, self.position)
        self.position += 4
        self.size -= 4
        return single[0]

    def read_string(self):
        if self.size < 0:
            raise MemoryError("To little data for string")
        length, bytes_consumed = self.read_string_length()

        if self.size < length + bytes_consumed:
            raise MemoryError("To little data for string")

        result = str(self.buffer[self.position + bytes_consumed:self.position + bytes_consumed + length], 'utf-8')

        self.size -= bytes_consumed + length
        self.position += bytes_consumed + length

        return result

    def read_string_length(self):
        length = 0
        byte_pos = 0

        while byte_pos in range(5):
            if byte_pos >= self.size:
                raise MemoryError("To little space for string")
            length_part = self.buffer[self.position + byte_pos]
            length = length | (length_part & 0x7f) << byte_pos * 7
            if not length_part & 0x80:
                break
            byte_pos += 1
        return length, byte_pos + 1

    def cut(self, payload_length: int):
        current_pos = self.position
        self.position += payload_length
        self.size -= payload_length
        return BinaryMemoryReader(self.buffer, current_pos)

    def dump(self):
        column = 0;
        for b in self.buffer[self.position:]:
            print("{0:02x} ".format(b), end='')
            column = column + 1
            if column >= 16:
                column = 0
                print()
        print()
