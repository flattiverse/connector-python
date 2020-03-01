#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-09-24
#
import string
import hashlib
import asyncio
import socket

from Cryptodome import Random
from Cryptodome.Cipher import AES

from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader
from flattiverse.connector.packet import Packet

HOST = 'galaxy.flattiverse.com'
PORT = 80


class Connection:
    BUFFER_SIZE = 262144

    def __init__(self):
        self.receiver_loop = None
        self.buffer = bytearray()
        self.plain = bytearray()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_aes = None
        self.send_aes = None
        self.packets_received = None

    def connect(self, user, password):
        client_iv = self.generate_client_initialization_vector()
        user_hash = self.generate_user_hash(user)
        initialization_packet_data = self.fill_in_initialization_packet(client_iv, user_hash)

        self.socket.connect((HOST, PORT))
        self.socket.sendall(initialization_packet_data)

        server_iv, random_challenge = self.receive_challenge()

        password_hash = self.hash_password(user, password)
        self.send_aes = AES.new(password_hash, AES.MODE_CBC, client_iv)
        self.recv_aes = AES.new(password_hash, AES.MODE_CBC, server_iv)

        response = self.generate_response(self.recv_aes, self.send_aes, random_challenge)
        self.socket.sendall(response)

        server_protocol_version = self.read_server_protocol_version()
        # print("Version: ", server_protocol_version)

        if server_protocol_version != 1:
            raise Exception("Wrong protocol version: " + str(server_protocol_version) + " instead of 1")

        asyncio.create_task(self.packet_receiver_loop())

    @staticmethod
    def generate_client_initialization_vector():
        # return bytearray(16)
        # return os.urandom(16)
        return Random.get_random_bytes(16)

    @staticmethod
    def generate_user_hash(user: string):
        user_bytes = bytes(user.lower(), 'utf-8')
        return hashlib.sha256(user_bytes).digest()

    def fill_in_initialization_packet(self, client_iv, user_hash):
        initialization_packet = bytearray(48)
        initialization_packet[:15] = client_iv
        initialization_packet[16:] = user_hash
        self.xor(client_iv, 0, initialization_packet, 16, 16)
        self.xor(client_iv, 0, initialization_packet, 32, 16)
        return initialization_packet

    @staticmethod
    def xor(src: bytearray, src_pos, dest: bytearray, dest_pos, length):
        for p in range(length):
            dest[dest_pos + p] ^= src[src_pos + p]

    def receive_challenge(self):
        packet_data = self.socket.recv(64)
        server_iv = packet_data[0:16]
        random_challenge = packet_data[16:48]
        return server_iv, random_challenge

    @staticmethod
    def hash_password(user, password):
        s_data = hashlib.sha512(bytes(user.lower(), 'utf-8')).digest()
        p_data = hashlib.sha512(bytes(password, 'utf-8')).digest()

        slowness = bytearray(80000000)
        for s_pos in range(0, 80000000, 80):
            slowness[s_pos:] = p_data[48:56]
            slowness[s_pos + 8:] = s_data[0:64]
            slowness[s_pos + 72:] = p_data[56:64]

        key = p_data[0:32]
        iv = s_data[32:48]
        aes = AES.new(key, AES.MODE_CBC, iv)

        for amount in range(7):
            aes.encrypt(slowness, slowness)

        iv = aes.encrypt(slowness[0:16])
        return iv

    def generate_response(self, recv_aes, send_aes, random_challenge):
        output_buffer = bytearray(recv_aes.decrypt(random_challenge[0:32]))
        self.xor(output_buffer[16:32], 0, output_buffer, 0, 16)
        response = send_aes.encrypt(output_buffer[0:16])
        return response

    def read_server_protocol_version(self):
        server_answer = self.socket.recv(16)
        server_protocol_version = server_answer[14] + server_answer[15] * 256
        return server_protocol_version

    async def packet_receiver_loop(self):
        # self.socket.setblocking(False)
        chunk = self.socket.recv(self.BUFFER_SIZE)
        self.completed(chunk)

    def completed(self, chunk: bytes):
        self.buffer = self.buffer + chunk

        # At least one chunk of 16 byte received
        if len(self.buffer) > 15:
            number_of_decryptable_bytes = len(self.buffer) - len(self.buffer) % 16
            plain_chunk = bytearray(self.recv_aes.decrypt(self.buffer[0:number_of_decryptable_bytes]))
            self.plain += plain_chunk

            reader = BinaryMemoryReader(self.plain, 0, len(self.plain))
            packets = []
            packet = Packet()

            while packet.parse(reader):
                if not packet.is_out_of_band:
                    packets.append(packet)
                    packet = Packet()

            if len(packets) > 0 and self.packets_received:
                self.packets_received(packets)

            self.buffer = self.buffer[reader.position:]
